"""
Module for integrating tribal boundaries into the risk assessment application.

County weights are pre-computed from a GeoPandas spatial overlay between:
- Wisconsin tribal boundary polygons (reservation + off-reservation trust land)
- Wisconsin county polygons (Census TIGER/Line, 72 counties)

Both reservation and off-reservation trust land features are included in the
combined weight calculation, weighted by land area. Separate reservation-only
and trust-land-only weight dictionaries are available for transparency and
future domain-specific use.

Weights are pre-computed offline rather than at runtime to avoid startup
overhead. To recompute them, run the compute_geometric_weights() function in
this module with updated GeoJSON data.

Known limitations:
- Demographic data (Census, SVI) is still sourced at the county level, not
  at the tribal AIANNH geography level. This is the most significant remaining
  source of inaccuracy for tribal risk scores.
- Sokaogon Chippewa Community (Mole Lake) does not appear in the filtered
  tribal boundaries GeoJSON. Its weights reflect its known geographic location
  (entirely within Forest County) rather than a computed spatial overlay.
- ACS margins of error are elevated for tribes with small enrolled populations
  (particularly Sokaogon and Red Cliff). This limitation is documented in the
  methodology.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
import shapely.geometry as geometry
from shapely.geometry import Point, shape

logger = logging.getLogger(__name__)

TRIBAL_BOUNDARIES_FILE = "data/tribal/wisconsin_tribal_boundaries_filtered.geojson"
WISCONSIN_COUNTIES_FILE = "data/tribal/wisconsin_counties.geojson"

TRIBAL_JURISDICTION_IDS = {
    "Bad River Band of Lake Superior Chippewa": "T01",
    "Forest County Potawatomi Community": "T02",
    "Ho-Chunk Nation": "T03",
    "Lac Courte Oreilles Band of Lake Superior Chippewa": "T04",
    "Lac du Flambeau Band of Lake Superior Chippewa": "T05",
    "Menominee Indian Tribe of Wisconsin": "T06",
    "Oneida Nation": "T07",
    "Red Cliff Band of Lake Superior Chippewa": "T08",
    "Sokaogon Chippewa Community (Mole Lake)": "T09",
    "St. Croix Chippewa Indians of Wisconsin": "T10",
    "Stockbridge-Munsee Community": "T11"
}

# Area-weighted county weights for each tribal jurisdiction, combining
# reservation land and off-reservation trust land.
# Source: GeoPandas spatial overlay, EPSG:3174 (Great Lakes Albers, area-preserving).
# Weights sum to 1.0 per tribe. Counties contributing less than 0.5% of total
# tribal land area are excluded as boundary slivers.
COMPUTED_TRIBAL_COUNTY_WEIGHTS = {
    "T01": {"Ashland": 0.9249, "Iron": 0.0474, "Forest": 0.0277},
    "T02": {"Forest": 0.9861, "Oconto": 0.0083, "Fond du Lac": 0.0056},
    "T03": {
        "Jackson": 0.2243, "Sauk": 0.1651, "Vernon": 0.1235,
        "Monroe": 0.1086, "Clark": 0.0951, "Shawano": 0.0797,
        "Wood": 0.0792, "Juneau": 0.0491, "Marathon": 0.0203,
        "Crawford": 0.0183, "Eau Claire": 0.0156, "Adams": 0.0122,
        "Trempealeau": 0.0089,
    },
    "T04": {"Sawyer": 1.0},
    "T05": {"Vilas": 0.82, "Iron": 0.1696, "Oneida": 0.0103},
    "T06": {"Menominee": 0.9943, "Shawano": 0.0057},
    "T07": {"Outagamie": 0.5915, "Brown": 0.4085},
    "T08": {"Bayfield": 1.0},
    "T09": {"Forest": 1.0},
    "T10": {"Burnett": 0.555, "Polk": 0.3892, "Barron": 0.0557},
    "T11": {"Shawano": 1.0},
}

# Reservation-only county weights (excludes off-reservation trust land features).
TRIBAL_RESERVATION_WEIGHTS = {
    "T01": {"Ashland": 0.9355, "Iron": 0.048, "Forest": 0.0165},
    "T02": {"Forest": 0.9844, "Oconto": 0.0098, "Marinette": 0.0058},
    "T03": {
        "Sauk": 0.7429, "Jackson": 0.173, "Monroe": 0.0237,
        "Juneau": 0.0376, "Wood": 0.0227,
    },
    "T04": {"Sawyer": 1.0},
    "T05": {"Vilas": 0.82, "Iron": 0.1696, "Oneida": 0.0103},
    "T06": {"Menominee": 1.0},
    "T07": {"Outagamie": 0.5898, "Brown": 0.4102},
    "T08": {"Bayfield": 1.0},
    "T09": {"Forest": 1.0},
    "T10": {"Burnett": 0.477, "Polk": 0.4565, "Barron": 0.0665},
    "T11": {"Shawano": 1.0},
}

# Off-reservation trust land county weights (where applicable).
# Tribes not listed here have no trust land features in the GeoJSON.
TRIBAL_TRUST_LAND_WEIGHTS = {
    "T01": {"Forest": 1.0},
    "T02": {"Forest": 0.9559, "Fond du Lac": 0.035, "Milwaukee": 0.0091},
    "T03": {
        "Jackson": 0.2394, "Vernon": 0.159, "Monroe": 0.133,
        "Clark": 0.1224, "Shawano": 0.1013, "Wood": 0.0955,
        "Juneau": 0.0525, "Marathon": 0.0261, "Crawford": 0.0235,
        "Eau Claire": 0.0201, "Adams": 0.0157, "Trempealeau": 0.0115,
    },
    "T04": {"Sawyer": 0.7474, "Burnett": 0.2091, "Washburn": 0.0435},
    "T06": {"Shawano": 0.9918, "Menominee": 0.0082},
    "T07": {"Outagamie": 0.9432, "Brown": 0.0568},
    "T08": {"Bayfield": 1.0},
    "T10": {"Burnett": 0.9591, "Polk": 0.0409},
    "T11": {"Shawano": 1.0},
}

# Fraction of each tribe's total land area that is off-reservation trust land.
# Computed from EPSG:3174 area calculations on the filtered GeoJSON features.
TRIBAL_TRUST_LAND_FRACTION = {
    "T01": 0.0113,
    "T02": 0.1592,
    "T03": 0.7846,
    "T04": 0.0091,
    "T05": 0.0,
    "T06": 0.0054,
    "T07": 0.005,
    "T08": 0.0362,
    "T09": 0.0,
    "T10": 0.1619,
    "T11": 0.1085,
}

# Fallback GeoJSON for when the actual boundaries file is unavailable.
INITIAL_TRIBAL_BOUNDARIES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-90.7, 46.5], [-90.5, 46.5], [-90.5, 46.3],
                    [-90.7, 46.3], [-90.7, 46.5]
                ]]
            },
            "properties": {
                "tribe": "Bad River Band of Lake Superior Chippewa",
                "jurisdiction_id": "T01"
            }
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-88.9, 45.5], [-88.7, 45.5], [-88.7, 45.3],
                    [-88.9, 45.3], [-88.9, 45.5]
                ]]
            },
            "properties": {
                "tribe": "Forest County Potawatomi Community",
                "jurisdiction_id": "T02"
            }
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-90.8, 44.3], [-90.6, 44.3], [-90.6, 44.1],
                    [-90.8, 44.1], [-90.8, 44.3]
                ]]
            },
            "properties": {
                "tribe": "Ho-Chunk Nation",
                "jurisdiction_id": "T03"
            }
        }
    ]
}


def initialize_tribal_boundaries():
    """
    Initialize tribal boundaries data if the file does not exist.

    Returns:
        bool: True if the file exists or was successfully created.
    """
    os.makedirs(os.path.dirname(TRIBAL_BOUNDARIES_FILE), exist_ok=True)
    if not os.path.exists(TRIBAL_BOUNDARIES_FILE):
        logger.info(f"Creating initial tribal boundaries file: {TRIBAL_BOUNDARIES_FILE}")
        try:
            with open(TRIBAL_BOUNDARIES_FILE, 'w') as f:
                json.dump(INITIAL_TRIBAL_BOUNDARIES, f)
            logger.info(
                f"Created initial tribal boundaries with "
                f"{len(INITIAL_TRIBAL_BOUNDARIES.get('features', []))} features"
            )
            return True
        except Exception as e:
            logger.error(f"Error creating initial tribal boundaries: {str(e)}")
            return False
    return True


def load_tribal_boundaries():
    """
    Load tribal boundaries from the GeoJSON file.

    Returns:
        dict: GeoJSON FeatureCollection with tribal boundary polygons.
    """
    initialize_tribal_boundaries()
    try:
        with open(TRIBAL_BOUNDARIES_FILE, 'r') as f:
            geojson_data = json.load(f)
        logger.info(f"Loaded {len(geojson_data.get('features', []))} tribal boundary features")
        return geojson_data
    except Exception as e:
        logger.error(f"Error loading tribal boundaries: {str(e)}")
        return INITIAL_TRIBAL_BOUNDARIES


def get_tribal_geometries() -> Dict[str, Any]:
    """
    Get merged geometry objects for each tribal jurisdiction.

    Returns:
        dict: Mapping of jurisdiction ID to merged GeoJSON geometry dict.
    """
    geojson_data = load_tribal_boundaries()
    if not geojson_data:
        return {}

    tribal_geometries = {}
    for feature in geojson_data.get('features', []):
        properties = feature.get('properties', {})
        tribe = properties.get('tribe')
        jurisdiction_id = TRIBAL_JURISDICTION_IDS.get(tribe)
        if not jurisdiction_id:
            continue
        try:
            if jurisdiction_id in tribal_geometries:
                existing = shape(tribal_geometries[jurisdiction_id])
                new = shape(feature.get('geometry'))
                merged = existing.union(new)
                try:
                    tribal_geometries[jurisdiction_id] = merged.__geo_interface__
                except Exception:
                    pass
            else:
                tribal_geometries[jurisdiction_id] = feature.get('geometry')
        except Exception as e:
            logger.error(f"Error processing tribal geometry for {jurisdiction_id}: {str(e)}")

    logger.info(f"Retrieved geometries for {len(tribal_geometries)} tribal jurisdictions")
    return tribal_geometries


def get_county_weights_for_tribe(jurisdiction_id: str) -> Dict[str, float]:
    """
    Return area-weighted county weights for a tribal jurisdiction.

    Weights are derived from a spatial overlay of tribal boundary polygons
    (reservation + off-reservation trust land) against Wisconsin county
    polygons. Counties contributing less than 0.5% of total tribal land area
    are excluded. Weights sum to 1.0.

    Args:
        jurisdiction_id: Tribal jurisdiction ID (e.g., 'T01').

    Returns:
        dict: Mapping of county name to fractional weight (0.0-1.0).
    """
    weights = COMPUTED_TRIBAL_COUNTY_WEIGHTS.get(jurisdiction_id)
    if not weights:
        logger.warning(f"No county weights for tribal jurisdiction {jurisdiction_id}")
        return {}
    return dict(weights)


def overlay_analysis(tribal_jurisdiction_id: str) -> Dict[str, float]:
    """
    Return area-weighted county overlap weights for a tribal jurisdiction.

    Args:
        tribal_jurisdiction_id: Tribal jurisdiction ID.

    Returns:
        dict: Mapping of county name to area-weighted overlap fraction.
    """
    return get_county_weights_for_tribe(tribal_jurisdiction_id)


def get_tribal_attributes(jurisdiction_id: str) -> Dict[str, Any]:
    """
    Return attributes for a tribal jurisdiction including county weights,
    trust land fraction, and primary county.

    Args:
        jurisdiction_id: Tribal jurisdiction ID.

    Returns:
        dict with keys:
            county_weights: Area-weighted county weights (reservation + trust land).
            reservation_weights: Reservation-only county weights.
            trust_land_weights: Trust-land-only county weights (may be empty).
            trust_land_fraction: Fraction of total land area that is off-reservation trust land.
            primary_county: County with the highest combined weight.
            total_weight: Sum of county weights (always 1.0 for valid jurisdictions).
            has_trust_land: True if the tribe has off-reservation trust land in the GeoJSON.
    """
    county_weights = get_county_weights_for_tribe(jurisdiction_id)
    if not county_weights:
        return {
            "county_weights": {},
            "reservation_weights": {},
            "trust_land_weights": {},
            "trust_land_fraction": 0.0,
            "primary_county": None,
            "total_weight": 0.0,
            "has_trust_land": False,
        }

    primary_county = max(county_weights.items(), key=lambda x: x[1])[0]
    trust_frac = TRIBAL_TRUST_LAND_FRACTION.get(jurisdiction_id, 0.0)

    return {
        "county_weights": county_weights,
        "reservation_weights": TRIBAL_RESERVATION_WEIGHTS.get(jurisdiction_id, county_weights),
        "trust_land_weights": TRIBAL_TRUST_LAND_WEIGHTS.get(jurisdiction_id, {}),
        "trust_land_fraction": trust_frac,
        "primary_county": primary_county,
        "total_weight": sum(county_weights.values()),
        "has_trust_land": trust_frac > 0.0,
    }


def calculate_tribal_risk(jurisdiction_id: str, risk_calculator_func) -> Dict[str, Any]:
    """
    Calculate risk scores for a tribal jurisdiction using area-weighted county data.

    County weights reflect the proportional overlap of the tribe's total land
    base (reservation + off-reservation trust land) with each Wisconsin county.
    Risk scores for each county are multiplied by the county's area weight and
    summed to produce the tribal composite score.

    Args:
        jurisdiction_id: Tribal jurisdiction ID.
        risk_calculator_func: Function that accepts a county name and returns
            a dict of risk type to numeric score.

    Returns:
        dict: Area-weighted composite risk scores for the tribal jurisdiction.
    """
    attributes = get_tribal_attributes(jurisdiction_id)
    county_weights = attributes["county_weights"]

    if not county_weights:
        logger.warning(f"No county weights for tribal jurisdiction {jurisdiction_id}")
        return {}

    risk_data: Dict[str, float] = {}
    for county, weight in county_weights.items():
        county_risk = risk_calculator_func(county)
        for risk_type, score in county_risk.items():
            if isinstance(score, (int, float)):
                risk_data[risk_type] = risk_data.get(risk_type, 0.0) + score * weight

    risk_data["tribal_status"] = True
    risk_data["tribal_counties"] = ','.join(county_weights.keys())
    risk_data["tribal_primary_county"] = attributes["primary_county"]
    risk_data["tribal_trust_land_fraction"] = attributes["trust_land_fraction"]
    risk_data["tribal_has_trust_land"] = attributes["has_trust_land"]

    for key in list(risk_data.keys()):
        if not isinstance(risk_data[key], (float, int, bool)):
            if key not in ("tribal_status", "tribal_counties", "tribal_primary_county",
                           "tribal_has_trust_land"):
                logger.warning(f"Removing non-numerical risk factor: {key}={risk_data[key]}")
                risk_data.pop(key)

    return risk_data


def compute_geometric_weights(save_results: bool = False) -> Dict[str, Dict[str, float]]:
    """
    Recompute area-weighted county overlap weights from the tribal and county
    GeoJSON files using GeoPandas spatial overlay.

    This function is not called at runtime. Run it manually when tribal boundary
    data changes and paste the output into COMPUTED_TRIBAL_COUNTY_WEIGHTS,
    TRIBAL_RESERVATION_WEIGHTS, TRIBAL_TRUST_LAND_WEIGHTS, and
    TRIBAL_TRUST_LAND_FRACTION above.

    Args:
        save_results: If True, print the computed dicts for copy-paste into source.

    Returns:
        dict: Combined area-weighted weights per jurisdiction ID.
    """
    try:
        import geopandas as gpd
        import warnings
    except ImportError:
        logger.error("GeoPandas is required to recompute geometric weights")
        return {}

    MIN_WEIGHT = 0.005

    with open(TRIBAL_BOUNDARIES_FILE) as f:
        tribal_gj = json.load(f)
    with open(WISCONSIN_COUNTIES_FILE) as f:
        county_gj = json.load(f)

    county_gdf = gpd.GeoDataFrame.from_features(
        county_gj['features'], crs='EPSG:4326'
    )[['NAME', 'geometry']].rename(columns={'NAME': 'county_name'})

    tribal_features = []
    for feat in tribal_gj['features']:
        props = feat.get('properties', {})
        tribe = props.get('tribe')
        jid = TRIBAL_JURISDICTION_IDS.get(tribe)
        namelsad = props.get('namelsad', '')
        is_trust = 'trust land' in namelsad.lower() or 'off-reservation' in namelsad.lower()
        if jid:
            tribal_features.append({
                'jurisdiction_id': jid, 'tribe': tribe,
                'namelsad': namelsad, 'is_trust_land': is_trust,
                'geometry': shape(feat['geometry'])
            })

    tribal_gdf = gpd.GeoDataFrame(tribal_features, crs='EPSG:4326')
    county_proj = county_gdf.to_crs('EPSG:3174')
    tribal_proj = tribal_gdf.to_crs('EPSG:3174')

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        overlaps = gpd.overlay(tribal_proj, county_proj, how='intersection')
    overlaps['overlap_area_m2'] = overlaps.geometry.area

    combined = {}
    reservation = {}
    trust = {}
    trust_frac = {}

    for jid in sorted(set(overlaps['jurisdiction_id'])):
        rows = overlaps[overlaps['jurisdiction_id'] == jid]
        total = rows['overlap_area_m2'].sum()

        def make_weights(subset):
            county_totals = subset.groupby('county_name')['overlap_area_m2'].sum()
            w = (county_totals / county_totals.sum()).to_dict()
            w = {c: v for c, v in w.items() if v >= MIN_WEIGHT}
            t = sum(w.values())
            return {c: round(v / t, 4) for c, v in w.items()}

        combined[jid] = make_weights(rows)

        res_rows = rows[~rows['is_trust_land']]
        if len(res_rows):
            reservation[jid] = make_weights(res_rows)

        tr_rows = rows[rows['is_trust_land']]
        if len(tr_rows):
            trust[jid] = make_weights(tr_rows)

        tribal_proj_jid = tribal_proj[tribal_proj['jurisdiction_id'] == jid]
        total_area = tribal_proj_jid['geometry'].area.sum()
        trust_area = tribal_proj_jid[tribal_proj_jid['is_trust_land']]['geometry'].area.sum()
        trust_frac[jid] = round(float(trust_area / total_area), 4) if total_area > 0 else 0.0

    if save_results:
        logger.info("COMPUTED_TRIBAL_COUNTY_WEIGHTS = " + repr(combined))
        logger.info("TRIBAL_RESERVATION_WEIGHTS = " + repr(reservation))
        logger.info("TRIBAL_TRUST_LAND_WEIGHTS = " + repr(trust))
        logger.info("TRIBAL_TRUST_LAND_FRACTION = " + repr(trust_frac))

    return combined
