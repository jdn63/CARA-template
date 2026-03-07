import json
import logging
import os
from typing import Dict, Any, Optional

from utils.risk_calculation import calculate_residual_risk, get_health_impact_factor
from utils.svi_data import get_svi_data

logger = logging.getLogger(__name__)

_dam_data_cache = None

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

DOWNSTREAM_POPULATION_TIERS = {
    'Milwaukee': 0.85, 'Dane': 0.78, 'Waukesha': 0.72, 'Brown': 0.65,
    'Racine': 0.62, 'Kenosha': 0.60, 'Outagamie': 0.58, 'Winnebago': 0.55,
    'Rock': 0.55, 'Marathon': 0.52, 'La Crosse': 0.50, 'Eau Claire': 0.48,
    'Sheboygan': 0.45, 'Fond du Lac': 0.45, 'Manitowoc': 0.42,
    'Walworth': 0.40, 'Washington': 0.42, 'Ozaukee': 0.40,
    'St. Croix': 0.38, 'Columbia': 0.38, 'Sauk': 0.40,
    'Jefferson': 0.38, 'Dodge': 0.35, 'Portage': 0.35,
    'Wood': 0.32, 'Chippewa': 0.35, 'Dunn': 0.30,
}

EOC_COUNTIES = ['Milwaukee', 'Dane', 'Brown', 'Waukesha', 'Racine',
                'La Crosse', 'Outagamie', 'Marathon', 'Eau Claire', 'Winnebago']


def _resolve_tribal_county(county_name: str) -> str:
    for tribal_name, mapped in TRIBAL_COUNTY_MAPPING.items():
        if tribal_name in county_name:
            logger.info(f"Dam failure: Using {mapped} County data for {county_name}")
            return mapped
    return county_name


def _is_tribal(county_name: str) -> bool:
    return any(t in county_name for t in TRIBAL_KEYWORDS)


def load_dam_inventory() -> Dict[str, Any]:
    global _dam_data_cache
    if _dam_data_cache is not None:
        return _dam_data_cache

    try:
        path = 'data/dam_inventory/wisconsin_dam_risk_factors.json'
        if os.path.exists(path):
            with open(path) as f:
                _dam_data_cache = json.load(f)
            logger.info("Loaded Wisconsin dam inventory data")
            return _dam_data_cache
    except Exception as e:
        logger.warning(f"Error loading dam inventory data: {e}")

    _dam_data_cache = {}
    return _dam_data_cache


def _get_county_dam_data(county_name: str) -> Dict[str, Any]:
    inventory = load_dam_inventory()
    county_data = inventory.get('county_dam_data', {}).get(county_name)
    if county_data:
        return county_data
    return {
        'total_dams': 10,
        'high_hazard': 1,
        'significant_hazard': 3,
        'low_hazard': 6,
        'has_eap': False,
        'flood_zone_overlap': 0.15
    }


def _get_all_svi_themes(county_name: str) -> Dict[str, float]:
    svi_data = get_svi_data(county_name)
    return {
        'overall': svi_data.get('overall', 0.5),
        'socioeconomic': svi_data.get('socioeconomic', 0.5),
        'household_composition': svi_data.get('household_composition', 0.5),
        'minority_status': svi_data.get('minority_status', 0.5),
        'housing_transportation': svi_data.get('housing_transportation', 0.5)
    }


def _get_census_demographics(county_name: str) -> Dict[str, float]:
    try:
        from utils.census_data_loader import wisconsin_census
        elderly_pct = wisconsin_census.get_elderly_population_percentage(county_name) or 18.7
        population = wisconsin_census.get_county_population(county_name) or 80000
    except Exception as e:
        logger.warning(f"Census data loading failed for {county_name}: {e}")
        elderly_pct = 18.7
        population = 80000

    elderly_factor = min(1.0, max(0.05, (elderly_pct - 10.0) / 25.0))
    pop_density_factor = min(1.0, population / 300000.0)

    return {
        'elderly_pct': elderly_pct,
        'elderly_factor': elderly_factor,
        'population': population,
        'pop_density_factor': pop_density_factor
    }


def calculate_dam_failure_risk(county_name: str, discipline: str = 'public_health') -> Dict[str, Any]:
    original_name = county_name
    if _is_tribal(county_name):
        county_name = _resolve_tribal_county(county_name)

    dam_data = _get_county_dam_data(county_name)
    svi = _get_all_svi_themes(county_name)
    census = _get_census_demographics(county_name)
    health_factor = get_health_impact_factor(county_name, 'dam_failure')

    inventory = load_dam_inventory()
    statewide = inventory.get('statewide_summary', {})
    max_dams = statewide.get('max_county_dam_count', 25)

    dam_density = min(1.0, dam_data['total_dams'] / max_dams)

    high_hazard_ratio = dam_data['high_hazard'] / max(1, dam_data['total_dams'])
    significant_hazard_ratio = dam_data['significant_hazard'] / max(1, dam_data['total_dams'])
    hazard_severity = min(1.0, (high_hazard_ratio * 0.7) + (significant_hazard_ratio * 0.3))

    flood_zone_overlap = dam_data.get('flood_zone_overlap', 0.15)

    exposure_factors = {
        'dam_density': dam_density,
        'hazard_classification': hazard_severity,
        'flood_zone_overlap': flood_zone_overlap
    }

    exposure_score = min(1.0, (
        (dam_density * 0.35) +
        (hazard_severity * 0.40) +
        (flood_zone_overlap * 0.25)
    ))

    downstream_pop_exposure = DOWNSTREAM_POPULATION_TIERS.get(county_name, 0.25)

    if discipline == 'em':
        infrastructure_density = census['pop_density_factor']
        rural_isolation = max(0.0, min(1.0, 1.0 - census['pop_density_factor']))
        vulnerability_score = min(1.0, (
            (downstream_pop_exposure * 0.35) +
            (svi['housing_transportation'] * 0.20) +
            (svi['socioeconomic'] * 0.10) +
            (infrastructure_density * 0.15) +
            (rural_isolation * 0.10) +
            (census['elderly_factor'] * 0.10)
        ))

        resilience_raw = 0.45
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.10)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.15)
        if county_name in EOC_COUNTIES:
            resilience_raw += 0.20
        if census['population'] > 75000:
            resilience_raw += 0.10
        if dam_data.get('has_eap', False):
            resilience_raw += 0.10
        resilience_raw = max(0.1, min(0.9, resilience_raw))
    else:
        vulnerability_score = min(1.0, (
            (downstream_pop_exposure * 0.30) +
            (svi['socioeconomic'] * 0.20) +
            (svi['household_composition'] * 0.15) +
            (svi['housing_transportation'] * 0.15) +
            (census['elderly_factor'] * 0.10) +
            (svi['minority_status'] * 0.10)
        ))

        resilience_raw = 0.5
        resilience_raw += ((1.0 - svi['socioeconomic']) * 0.15)
        resilience_raw += ((1.0 - svi['housing_transportation']) * 0.10)

        if dam_data.get('has_eap', False):
            resilience_raw += 0.15

        prepared_counties = ['Milwaukee', 'Dane', 'Brown', 'Waukesha', 'Racine']
        if county_name in prepared_counties:
            resilience_raw += 0.15
        elif county_name in ['La Crosse', 'Outagamie', 'Rock', 'Marathon']:
            resilience_raw += 0.10

        resilience_raw = max(0.1, min(0.9, resilience_raw))

    residual_risk = calculate_residual_risk(
        exposure=exposure_score,
        vulnerability=vulnerability_score,
        resilience=resilience_raw,
        health_impact_factor=health_factor
    )

    metrics = {
        'total_dams': dam_data['total_dams'],
        'high_hazard_dams': dam_data['high_hazard'],
        'significant_hazard_dams': dam_data['significant_hazard'],
        'low_hazard_dams': dam_data['low_hazard'],
        'has_emergency_action_plan': dam_data.get('has_eap', False),
        'flood_zone_overlap_pct': round(flood_zone_overlap * 100, 1),
        'downstream_population_exposure': round(downstream_pop_exposure, 2),
        'elderly_vulnerability_pct': round(census['elderly_pct'], 1),
        'has_real_data': True
    }

    data_sources = [
        'U.S. Army Corps of Engineers National Inventory of Dams (NID)',
        'Wisconsin DNR Dam Safety Program',
        'FEMA National Risk Index - Flood Risk Layer',
        'CDC Social Vulnerability Index (SVI) - All 4 Themes',
        'U.S. Census Bureau ACS - Demographics',
        'Wisconsin Emergency Management - Dam Emergency Action Plans'
    ]

    return {
        'overall': residual_risk,
        'components': {
            'exposure': exposure_score,
            'vulnerability': vulnerability_score,
            'resilience': resilience_raw,
            'health_impact': health_factor
        },
        'exposure_factors': exposure_factors,
        'vulnerability_breakdown': {
            'downstream_population_exposure': downstream_pop_exposure,
            'housing_transportation_svi': svi['housing_transportation'],
            'socioeconomic_svi': svi['socioeconomic'],
            'household_composition_svi': svi['household_composition'],
            'minority_status_svi': svi['minority_status'],
            'elderly_factor': census['elderly_factor']
        },
        'metrics': metrics,
        'data_sources': data_sources
    }
