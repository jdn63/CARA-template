# CARA - Comprehensive Automated Risk Assessment (Template)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A generalized template for building comprehensive geospatial health and emergency preparedness risk assessment platforms. Designed to be adapted by any jurisdiction -- state, county, tribal nation, or international context.

This repository is a starting point. It includes 5 example placeholder jurisdictions and clearly marked modules for you to replace with your own data sources, jurisdictions, and regional groupings.

For the production Wisconsin implementation, see [CARA](https://github.com/jdn63/CARA).

## Quick Start

1. Clone or use this template to create your own repository
2. Set up a PostgreSQL database and set the DATABASE_URL environment variable
3. Run the application with Python 3.11+
4. The app will start with 5 example jurisdictions (Example County A through E)

## Adapting CARA to Your Jurisdiction

The adaptation process is documented in two workshop guides included in docs/:

- **Technical Workshop Guide** (docs/CARA_Adaptation_Workshop_Guide.md) -- A 5-day facilitator guide for developers, covering file-by-file customization with hands-on exercises
- **Replit Workshop Guide** (docs/CARA_Replit_Workshop_Guide.md) -- A 3-day facilitator guide for non-technical users, using prompt-driven development on the Replit platform

### Key Files to Customize

| File | What to Change |
|------|---------------|
| utils/jurisdictions_code.py | Replace 5 example jurisdictions with your own |
| utils/jurisdiction_mapping_code.py | Map jurisdiction IDs to county/district names |
| data/census/example_demographics.csv | Population data for your jurisdictions |
| data/census/example_housing_data.csv | Housing data for your jurisdictions |
| data/svi/example_svi_data.json | Social vulnerability indices for your jurisdictions |
| data/herc/example_regions.json | Regional groupings (optional) |
| config/county_baselines.yaml | Baseline risk scores for your jurisdictions |
| agencies.txt | List of health departments/agencies |
| example_health_departments.json | Health department details |

### Wisconsin-Specific Modules

The following modules are marked with WISCONSIN-SPECIFIC MODULE header blocks. They contain Wisconsin data sources and integrations that you should replace with your own:

- utils/dhs_data.py -- State health department API integration
- utils/wisconsin_dhs_scraper.py -- State health department report scraping
- utils/wisconsin_climate_data.py -- State climate normals
- utils/wisconsin_mapping.py -- City-to-county mapping
- utils/wem_data.py -- Emergency management data
- utils/wem_integration.py -- Emergency management system integration
- utils/wha_integration.py -- Hospital association integration
- utils/herc_data.py -- Regional coalition data
- utils/herc_risk_aggregator.py -- Regional risk aggregation
- utils/tribal_boundaries.py -- Tribal jurisdiction boundaries

These modules are functional and will return graceful defaults when their Wisconsin-specific data is not present.

## Architecture

- **Backend**: Flask (Python) with PostgreSQL and PostGIS
- **Frontend**: Jinja2 templates with Bootstrap 5
- **Visualization**: Chart.js for charts, Folium for interactive maps
- **Data Processing**: Pandas, NumPy, GeoPandas
- **Scheduling**: APScheduler for automated data refreshes

## Risk Assessment Framework

CARA uses the PHRAT (Public Health Risk Assessment Tool) formula:

**Overall Risk = sqrt(sum(w_i * Risk_i^2))** with p=2

### Risk Domains (5 Primary + 2 Supplementary)

1. Natural Hazards (flood, tornado, winter storm, thunderstorm)
2. Infectious Disease (influenza, COVID-19, RSV)
3. Active Shooter
4. Extreme Heat
5. Air Quality
6. Cybersecurity (supplementary, proxy-based)
7. Utilities/Infrastructure (supplementary, proxy-based)

Each domain uses an Exposure-Vulnerability-Resilience (EVR) framework adjusted by CDC Social Vulnerability Index data.

## Data Integration

CARA integrates data from multiple authoritative sources:

- **OpenFEMA APIs** (keyless) -- Disaster declarations, NFIP claims, hazard mitigation projects
- **NOAA NCEI Storm Events** -- Historical storm event data
- **FEMA National Risk Index** -- Baseline hazard risk indices
- **CDC Social Vulnerability Index** -- Community vulnerability factors
- **EPA AirNow API** -- Air quality monitoring
- **Local Census data** -- Demographics and housing from CSV files

All external data is pre-fetched by scheduled jobs and cached in PostgreSQL, so no external API calls occur during user assessments.

## Export Features

- **Kaiser Permanente HVA Export** -- Auto-populates the official KP HVA template (.xlsm) with CARA risk data
- **PDF Action Plans** -- Customized preparedness recommendations
- **GIS Export** -- Geospatial data export for mapping applications

## Configuration

- config/risk_weights.yaml -- Domain weights, temporal weights, SVI adjustment factors
- config/county_baselines.yaml -- Jurisdiction-specific baseline scores
- data/config/scheduler_config.json -- Data refresh schedules

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPLv3). See LICENSE for details.

## Citation

If you use CARA in your work, please cite it using the information in CITATION.cff.

## Contributing

See CONTRIBUTING.md for guidelines on contributing to this project.
