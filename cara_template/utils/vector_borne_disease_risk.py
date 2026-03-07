import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from utils.risk_calculation import calculate_residual_risk, get_health_impact_factor
from utils.svi_data import get_svi_data

logger = logging.getLogger(__name__)

_baseline_data_cache = None
_real_data_cache = {}

TRIBAL_COUNTY_MAPPING = {
    'HoChunk': 'Jackson',
    'Ho-Chunk': 'Jackson',
    'Menominee': 'Menominee',
    'Oneida': 'Brown',
    'Lac du Flambeau': 'Vilas',
    'Bad River': 'Ashland',
    'Red Cliff': 'Bayfield',
    'Potawatomi': 'Forest',
    'St. Croix': 'Burnett',
    'Sokaogon': 'Forest',
    'Lac Courte Oreilles': 'Sawyer'
}

TRIBAL_KEYWORDS = ['Ho-Chunk', 'HoChunk', 'Menominee', 'Oneida', 'Lac du Flambeau',
                   'Bad River', 'Red Cliff', 'Potawatomi', 'St. Croix', 'Sokaogon',
                   'Lac Courte Oreilles']


def _is_tribal(county_name: str) -> bool:
    return any(t in county_name for t in TRIBAL_KEYWORDS)


def _resolve_tribal_county(county_name: str) -> str:
    for tribal_name, mapped in TRIBAL_COUNTY_MAPPING.items():
        if tribal_name in county_name:
            logger.info(f"Using {mapped} County data for {county_name}")
            return mapped
    return county_name


def load_baseline_data() -> Dict[str, Any]:
    global _baseline_data_cache
    if _baseline_data_cache is not None:
        return _baseline_data_cache

    try:
        path = 'data/disease/wisconsin_vector_borne_baseline.json'
        if os.path.exists(path):
            with open(path) as f:
                _baseline_data_cache = json.load(f)
            logger.info("Loaded vector-borne disease baseline data")
            return _baseline_data_cache
    except Exception as e:
        logger.warning(f"Error loading vector-borne disease baseline data: {e}")

    _baseline_data_cache = {}
    return _baseline_data_cache


def _get_tier_score(tier: str, baseline: Dict[str, Any]) -> float:
    tier_scores = baseline.get('tier_scores', {})
    return tier_scores.get(tier, 0.45)


def _get_deer_density_score(density: str, baseline: Dict[str, Any]) -> float:
    density_scores = baseline.get('deer_density_scores', {})
    return density_scores.get(density, 0.45)


def _get_seasonal_factor() -> float:
    month = datetime.now().month

    tick_active = [4, 5, 6, 7, 8, 9, 10]
    tick_peak = [5, 6, 7]
    mosquito_active = [6, 7, 8, 9]
    mosquito_peak = [7, 8]

    tick_factor = 0.0
    if month in tick_peak:
        tick_factor = 1.0
    elif month in tick_active:
        tick_factor = 0.6
    else:
        tick_factor = 0.15

    mosquito_factor = 0.0
    if month in mosquito_peak:
        mosquito_factor = 1.0
    elif month in mosquito_active:
        mosquito_factor = 0.6
    else:
        mosquito_factor = 0.10

    combined = (tick_factor * 0.75) + (mosquito_factor * 0.25)
    return max(0.15, min(1.0, combined))


def _get_climate_multiplier(baseline: Dict[str, Any]) -> float:
    climate = baseline.get('climate_impact', {})
    tick_mult = climate.get('tick_range_expansion', {}).get('multiplier', 1.15)
    season_mult = climate.get('extended_season', {}).get('multiplier', 1.10)
    mosquito_mult = climate.get('mosquito_habitat', {}).get('multiplier', 1.12)

    combined = (tick_mult * 0.50) + (season_mult * 0.30) + (mosquito_mult * 0.20)
    return combined


def get_all_svi_themes(county_name: str) -> Dict[str, float]:
    svi_data = get_svi_data(county_name)
    return {
        'overall': svi_data.get('overall', 0.5),
        'socioeconomic': svi_data.get('socioeconomic', 0.5),
        'household_composition': svi_data.get('household_composition', 0.5),
        'minority_status': svi_data.get('minority_status', 0.5),
        'housing_transportation': svi_data.get('housing_transportation', 0.5)
    }


def get_census_demographics(county_name: str) -> Dict[str, float]:
    try:
        from utils.census_data_loader import wisconsin_census
        elderly_pct = wisconsin_census.get_elderly_population_percentage(county_name) or 18.7
        population = wisconsin_census.get_county_population(county_name) or 80000
    except Exception as e:
        logger.warning(f"Census data loading failed for {county_name}: {e}")
        elderly_pct = 18.7
        population = 80000

    elderly_factor = min(1.0, max(0.05, (elderly_pct - 10.0) / 25.0))
    rural_factor = min(1.0, max(0.0, 1.0 - (population / 300000.0)))

    return {
        'elderly_pct': elderly_pct,
        'elderly_factor': elderly_factor,
        'population': population,
        'rural_factor': rural_factor
    }


def calculate_vector_borne_disease_risk(county_name: str, discipline: str = 'public_health') -> Dict[str, Any]:
    original_name = county_name
    if _is_tribal(county_name):
        county_name = _resolve_tribal_county(county_name)

    baseline = load_baseline_data()
    county_data = baseline.get('county_baselines', {}).get(county_name, None)

    if county_data is None:
        logger.warning(f"No vector-borne disease baseline for {county_name}, using defaults")
        county_data = {
            'lyme_tier': 'moderate',
            'wnv_tier': 'low',
            'forest_cover_pct': 30,
            'deer_density': 'moderate',
            'outdoor_workforce_pct': 10
        }

    svi = get_all_svi_themes(county_name)
    census = get_census_demographics(county_name)
    seasonal_factor = _get_seasonal_factor()
    climate_mult = _get_climate_multiplier(baseline)

    lyme_score = _get_tier_score(county_data['lyme_tier'], baseline)
    wnv_score = _get_tier_score(county_data['wnv_tier'], baseline)
    forest_cover_factor = min(1.0, county_data['forest_cover_pct'] / 100.0)
    deer_density_score = _get_deer_density_score(county_data['deer_density'], baseline)
    outdoor_workforce_factor = min(1.0, county_data['outdoor_workforce_pct'] / 25.0)

    case_rate_composite = (lyme_score * 0.65) + (wnv_score * 0.35)
    land_cover_factor = (forest_cover_factor * 0.60) + (deer_density_score * 0.40)

    exposure_factors = {
        'historical_case_rates': case_rate_composite,
        'land_cover_risk': land_cover_factor,
        'seasonal_activity': seasonal_factor,
        'climate_trend': min(1.0, case_rate_composite * climate_mult) - case_rate_composite
    }

    exposure_score = min(1.0, (
        (exposure_factors['historical_case_rates'] * 0.45) +
        (exposure_factors['land_cover_risk'] * 0.25) +
        (exposure_factors['seasonal_activity'] * 0.15) +
        (exposure_factors['climate_trend'] * 0.15)
    ))

    if discipline == 'em':
        vulnerability_score = min(1.0, (
            (outdoor_workforce_factor * 0.25) +
            (census['elderly_factor'] * 0.20) +
            (census['rural_factor'] * 0.20) +
            (svi['socioeconomic'] * 0.15) +
            (svi['household_composition'] * 0.10) +
            (svi['minority_status'] * 0.10)
        ))

        resilience_raw = 0.45
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.10)
        resilience_raw += ((1.0 - census['rural_factor']) * 0.15)

        surveillance_counties = ['Milwaukee', 'Dane', 'Brown', 'Waukesha', 'La Crosse',
                                 'Marathon', 'Eau Claire', 'Outagamie', 'Winnebago']
        if county_name in surveillance_counties:
            resilience_raw += 0.20
        elif census['population'] > 50000:
            resilience_raw += 0.10

        resilience_raw = max(0.1, min(0.9, resilience_raw))
    else:
        vulnerability_score = min(1.0, (
            (outdoor_workforce_factor * 0.20) +
            (census['elderly_factor'] * 0.20) +
            (census['rural_factor'] * 0.15) +
            (svi['socioeconomic'] * 0.20) +
            (svi['household_composition'] * 0.15) +
            (svi['minority_status'] * 0.10)
        ))

        resilience_raw = 0.5
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.15)
        resilience_raw += ((1.0 - census['rural_factor']) * 0.10)

        well_resourced = ['Milwaukee', 'Dane', 'Brown', 'Waukesha', 'La Crosse']
        if county_name in well_resourced:
            resilience_raw += 0.20
        elif county_name in ['Marathon', 'Eau Claire', 'Outagamie', 'Winnebago', 'Rock']:
            resilience_raw += 0.10

        resilience_raw = max(0.1, min(0.9, resilience_raw))

    health_factor = 1.0
    try:
        health_factor = get_health_impact_factor(county_name, 'flood')
    except Exception:
        health_factor = 1.0

    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw,
        health_impact_factor=health_factor
    )

    season_label = _get_season_label()

    metrics = {
        'lyme_disease_tier': county_data['lyme_tier'],
        'west_nile_virus_tier': county_data['wnv_tier'],
        'forest_cover_pct': county_data['forest_cover_pct'],
        'deer_density': county_data['deer_density'],
        'outdoor_workforce_pct': county_data['outdoor_workforce_pct'],
        'seasonal_risk_level': season_label,
        'seasonal_factor': round(seasonal_factor, 2),
        'climate_trend_impact': f"+{int((climate_mult - 1.0) * 100)}%",
        'elderly_vulnerability_pct': round(census['elderly_pct'], 1),
        'diseases_assessed': ['Lyme Disease', 'West Nile Virus', 'Anaplasmosis', 'Ehrlichiosis']
    }

    data_sources = [
        'Wisconsin DHS Tick-Borne Disease Surveillance Reports',
        'CDC ArboNET West Nile Virus Surveillance',
        'USDA Forest Service NLCD Land Cover Data',
        'Wisconsin DNR Deer Population Estimates',
        'CDC Social Vulnerability Index (SVI)',
        'U.S. Census Bureau ACS Demographics',
        'NOAA/WICCI Climate Projections'
    ]

    return {
        'overall': residual_risk,
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw,
            'health_impact': health_factor,
            'climate_multiplier': climate_mult,
            'seasonal_factor': seasonal_factor
        },
        'exposure_factors': exposure_factors,
        'vulnerability_breakdown': {
            'outdoor_workforce_factor': outdoor_workforce_factor,
            'elderly_factor': census['elderly_factor'],
            'rural_factor': census['rural_factor'],
            'socioeconomic_svi': svi['socioeconomic'],
            'household_composition_svi': svi['household_composition'],
            'minority_status_svi': svi['minority_status']
        },
        'metrics': metrics,
        'data_sources': data_sources
    }


def _get_season_label() -> str:
    month = datetime.now().month
    if month in [5, 6, 7]:
        return 'Peak tick season'
    elif month in [4, 8, 9, 10]:
        return 'Active tick season'
    elif month in [7, 8]:
        return 'Peak mosquito season'
    elif month in [6, 9]:
        return 'Active mosquito season'
    elif month in [11, 12, 1, 2, 3]:
        return 'Low season (winter)'
    return 'Moderate activity'
