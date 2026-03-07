# CARA Template - Comprehensive Automated Risk Assessment

## Overview

CARA is a geospatial health and emergency preparedness risk assessment platform designed for state and regional public health departments. This template provides the full CARA framework for adaptation to your jurisdiction.

## Quick Start

Prerequisites:
- Python 3.11+
- PostgreSQL 14+ with PostGIS extension
- API keys: Census API, EPA AirNow (optional)

Setup:
1. Clone this repository
2. Copy .env.example to .env and configure your environment variables
3. Install dependencies: pip install -r requirements.txt
4. Initialize the database: python -c "from core import create_app; app = create_app(); app.app_context().__enter__()"
5. Run: gunicorn --bind 0.0.0.0:5000 --reload main:app

## Adaptation Guide

To adapt CARA for your state or region:

1. Jurisdiction Data (utils/jurisdictions_code.py):
   - Replace Wisconsin jurisdictions with your state's counties and health departments
   - Update jurisdiction IDs and mappings

2. Regional Structure (utils/herc_data.py):
   - Replace HERC regions with your state's health planning regions
   - Update county-to-region mappings

3. Risk Data Files (data/):
   - data/dam_inventory/ - Replace with your state's NID dam data
   - data/disease/ - Replace with your state's vector-borne disease baselines
   - data/census/ - Replace with your state's Census ACS data

4. Configuration (config/):
   - config/risk_weights.yaml - Adjust domain weights for your risk profile
   - config/county_baselines.yaml - Set baselines for your jurisdictions

5. Data Sources (utils/):
   - utils/wisconsin_dhs_scraper.py - Adapt for your state's health department data source
   - utils/noaa_storm_events.py - Update state filter from WISCONSIN
   - utils/openfema_data.py - Update state FIPS code
   - utils/svi_data.py - Update state FIPS code

6. Templates (templates/):
   - Update branding, state name references, and region names
   - Update map images in static/images/regions/

7. GeoJSON (static/geojson/):
   - Replace Wisconsin county boundaries with your state's boundaries

## Architecture

- Backend: Flask + PostgreSQL + APScheduler
- Frontend: Jinja2 + Bootstrap 5 + Folium maps
- Risk Framework: PHRAT (Public Health Risk Assessment Tool) with EVR (Exposure-Vulnerability-Resilience) methodology
- Data: Pre-cached architecture where all external APIs are fetched by scheduler with zero API calls during assessments

## Risk Domains (7 for PH, 8 for EM)

1. Natural Hazards (flood, tornado, winter storm, thunderstorm)
2. Health Metrics (infectious disease surveillance)
3. Active Shooter
4. Extreme Heat (climate-adjusted)
5. Air Quality
6. Dam Failure
7. Vector-Borne Disease
8. Utilities (EM discipline only)

## License

AGPLv3 - See LICENSE file
