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
3. Add dependencies: pip -r requirements.txt
4. Initialize the database
5. Run: gunicorn --bind 0.0.0.0:5000 --reload main:app

## Adaptation Guide

To adapt CARA for your state or region:

1. Jurisdiction Data (utils/jurisdictions_code.py):
   - Replace Wisconsin jurisdictions with your state's counties and health departments
   - Update jurisdiction IDs and mappings

2. Regional Structure (utils/herc_data.py):
   - Replace HERC regions with your state's health planning regions
   - Update regional groupings and metadata

3. Data Sources (data/ directory):
   - Replace county-level CSV files with your state's demographic data
   - Update Census tract data for your state's FIPS codes
   - Replace tribal jurisdiction data if applicable

4. Risk Configuration (config/):
   - risk_weights.yaml: Adjust domain weights for your jurisdiction's priorities
   - county_baselines.yaml: Set baseline scores for your counties

5. External APIs:
   - OpenFEMA: Update state filter from "Wisconsin" to your state
   - NOAA Storm Events: Update state filter
   - EPA AirNow: Update monitoring station coordinates
   - Dam Safety: Update to your state's dam inventory source

6. Templates (templates/):
   - Update state-specific references and branding
   - Modify regional dashboard labels

## Risk Domains

| Domain | Default Weight | Description |
|--------|---------------|-------------|
| Natural Hazards | 28% | Flood, tornado, winter storm, thunderstorm EVR assessment |
| Health Metrics | 17% | Infectious disease surveillance and vaccination rates |
| Active Shooter | 18% | Community violence risk assessment |
| Extreme Heat | 11% | Heat vulnerability and climate-adjusted risk |
| Air Quality | 12% | Environmental health and AQI assessment |
| Dam Failure | 7% | Dam infrastructure risk using state dam inventory with flood zone analysis |
| Vector-Borne Disease | 7% | Tick-borne and mosquito-borne illness surveillance |

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See the LICENSE file for details.

## Citation

If you use CARA in your work, please cite using the CITATION.cff file included in this repository.
