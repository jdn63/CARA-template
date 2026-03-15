# CARA - Comprehensive Automated Risk Assessment
<!-- Last updated: 2026-03-15 -->

A geospatial health and emergency preparedness risk assessment platform designed for Wisconsin public health departments, serving 95 jurisdictions including 11 tribal nations.

## Overview

CARA provides multi-domain risk scoring, scheduled data integration from authoritative sources, and actionable preparedness guidance to public health officials across Wisconsin. The platform enhances public health emergency response and strategic planning capabilities with data-driven insights aligned with CDC Public Health Emergency Preparedness (PHEP) capabilities.

Key features:
- All 95 Wisconsin public health jurisdictions (84 local health departments + 11 tribal nations) with 101 county-level entries for risk mapping across 7 HERC regions
- 7 primary risk domains (natural hazards, infectious disease, active shooter, extreme heat, air quality, dam failure, vector-borne disease) plus supplementary assessments modeled from proxy indicators (cybersecurity, utilities)
- Real data integration from OpenFEMA APIs, NOAA Storm Events Database, Wisconsin DHS, EPA AirNow, and local Census/FEMA NRI CSV files
- Performance-optimized with full dashboard context caching for near-instant load times after initial cache build
- Strategic Planning Mode for long-term risk assessment optimized for annual preparedness planning cycles
- Full integration with CDC Public Health Emergency Preparedness capabilities
- Automated action plans with customized preparedness recommendations and implementation timelines
- Interactive geospatial mapping, risk distribution charts, and trend analysis

## Architecture

Backend:
- Framework: Flask (Python) with Blueprint architecture and application factory pattern
- Database: PostgreSQL with PostGIS extension for geospatial data
- Data Processing: Pandas, NumPy, GeoPandas for data manipulation
- Scheduling: APScheduler for automated data refreshes
- APIs: RESTful integration with multiple government data sources

Frontend:
- Templates: Jinja2 with Bootstrap 5 responsive design
- Visualization: Folium for interactive mapping
- Accessibility: WCAG 2.1 AA compliant design with screen reader support
- Performance: Lazy loading, caching, and optimized asset delivery

## Quick Start

Prerequisites:
- Python 3.11+
- PostgreSQL with PostGIS extension
- Required API keys (see Configuration section)

Installation:

1. Clone the repository
```bash
git clone https://github.com/jdn63/CARA.git
cd CARA
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Initialize the database
```bash
python -c "from core import create_app; app = create_app(); app.app_context().push(); from core import db; db.create_all()"
```

5. Run the application
```bash
python main.py
```

The application will be available at http://localhost:5000

## Deployment

Render Deployment:

The project includes a render.yaml configuration file for easy deployment to Render.

1. Connect to GitHub: Link your Render account to your GitHub repository
2. Environment Variables: Set the following in Render dashboard:
   - DATABASE_URL: Your PostgreSQL connection string
   - SESSION_SECRET: Secure random string
   - AIRNOW_API_KEY: Your EPA AirNow API key
   - ENABLE_SCRAPERS: Set to 1 to enable DHS data scraping
3. Deploy: Render will automatically deploy using the configuration in render.yaml

The application uses Gunicorn with 2 workers and 120-second timeout for production-ready performance.

## Risk Assessment Framework

CARA employs a multi-dimensional risk assessment methodology.

Risk Domains (7 Primary + 2 Supplementary):

| Domain | Weight | Description |
|--------|--------|-------------|
| Natural Hazards | 28% | Flood, tornado, winter storm, thunderstorm (EVR framework with real NOAA/OpenFEMA data) |
| Health Metrics | 17% | Infectious disease surveillance and vaccination rates |
| Active Shooter | 18% | Community violence risk assessment |
| Extreme Heat | 11% | Heat vulnerability and climate-adjusted risk |
| Air Quality | 12% | Environmental health and AQI assessment |
| Dam Failure | 7% | Dam infrastructure risk using WI DNR Dam Safety Database (~4,100 active dams) with NFIP flood zone analysis |
| Vector-Borne Disease | 7% | Lyme disease, West Nile Virus, tick-borne illness surveillance |
| Cybersecurity | Supplementary | Critical infrastructure cyber threats (proxy indicators) |
| Utilities Risk | Supplementary | Electrical, water/sewer, supply chain, fuel shortage (proxy indicators) |

The 7 primary domains are aggregated using the PHRAT quadratic mean formula (p=2), which appropriately emphasizes higher-risk domains rather than averaging them away. Cybersecurity and Utilities are assessed separately as supplementary domains modeled from proxy indicators and are not included in the PHRAT composite score.

Temporal Framework (BSTA):
- Baseline (60%): Long-term structural risk factors
- Seasonal (25%): Predictable cyclical variations
- Trend (15%): Medium-term directional changes
- Acute (0%): Short-term event-driven spikes (Strategic Planning Mode)

Social Vulnerability Integration:

All risk calculations incorporate CDC Social Vulnerability Index (SVI) factors:
- Socioeconomic status
- Household composition and disability
- Minority status and language
- Housing type and transportation

## Configuration

Required API Keys:

Add these environment variables for full functionality:

```bash
AIRNOW_API_KEY=your_airnow_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
DATABASE_URL=postgresql://user:pass@localhost/cara_db
SESSION_SECRET=your_secure_session_secret
```

Data Sources:

CARA integrates with multiple authoritative data sources, all pre-fetched by scheduled background jobs and cached locally (no external API calls during user assessments):

- OpenFEMA APIs (keyless): Disaster Declarations Summaries v2, NFIP Redacted Claims v2, Hazard Mitigation Assistance Projects v4. Weekly refresh, PostgreSQL cache.
- NOAA NCEI Storm Events Database: Bulk CSV downloads of Wisconsin storm events (tornado, flood, thunderstorm, winter storm) with property damage, injuries, fatalities. Weekly refresh, local file cache.
- Wisconsin DHS: Disease surveillance and health metrics via Tableau dashboard scraping (cached).
- CDC: Social Vulnerability Index and PHEP guidelines.
- FEMA NRI: National Risk Index data (local CSV files).
- EPA AirNow: Air quality monitoring (daily scheduler cache, requires API key).
- NOAA/NWS: Heat forecasting and weather alerts.
- Census Bureau: Demographic and housing data (local CSV files).
- WI DNR Dam Safety Database: Wisconsin Repository of Dams (~4,100 active dams, weekly cache). USACE NID as fallback.

## Usage

Web Interface:
1. Home Page: Select from 95 Wisconsin jurisdictions
2. Dashboard: View comprehensive risk assessment with interactive mapping
3. Action Plans: Download customized preparedness recommendations
4. Methodology: Detailed documentation of risk calculation methods
5. HERC Integration: Regional health coordination dashboard

API Endpoints:

```
GET /api/historical-data/{jurisdiction_id}
GET /api/predictive-analysis/{jurisdiction_id}
GET /api/herc-region/{region_id}
GET /api/herc-regions
GET /api/wem-region/{region_id}
GET /api/wem-regions
GET /api/herc-boundaries
GET /api/wem-boundaries
GET /api/scheduler-status
POST /api/refresh-data/{source}
```

## Security

CARA implements comprehensive security measures:
- Environment-based secrets with no hardcoded API keys or credentials
- Input validation on all user inputs
- XSS protection with proper template escaping
- Parameterized database queries and connection pooling
- Rate limiting on API endpoints
- Content Security Policy headers
- Session cookie security (HttpOnly, SameSite, Secure)

## Data Scraping and Ethics

CARA includes a scraper for publicly accessible Wisconsin DHS respiratory surveillance data. The scraper is designed to be respectful and transparent:

- Opt-in by default: Scraping is disabled unless ENABLE_SCRAPERS=1 is explicitly set. In production, the application uses cached or fallback data.
- Caching with TTL: Fetched data is cached locally. Cache freshness is controlled by CACHE_TTL_HOURS (default: 24 hours).
- Rate-limited: A configurable delay (REQUEST_DELAY_SECONDS, default: 1.5s) is applied between requests. On 429 or 503 responses, the scraper backs off with exponential retry.
- Identified: All requests include a User-Agent header identifying the scraper and providing contact information.
- Public data only: The scraper accesses only publicly available DHS surveillance data. No authentication or restricted resources are accessed.

| Variable | Default | Description |
|----------|---------|-------------|
| ENABLE_SCRAPERS | 0 | Set to 1 to enable DHS scraping |
| CACHE_TTL_HOURS | 24 | Max age of cached data before re-fetch |
| REQUEST_DELAY_SECONDS | 1.5 | Delay between HTTP requests |
| REQUEST_MAX_RETRIES | 3 | Max retry attempts on transient errors |

## Contributing

We welcome contributions from the public health and emergency management community.

Development Setup:
1. Fork the repository
2. Create a feature branch: git checkout -b feature/your-feature
3. Make your changes and add tests
4. Commit your changes: git commit -m "Add your feature"
5. Push to the branch: git push origin feature/your-feature
6. Open a Pull Request

Code Style:
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include unit tests for new features

## Documentation

- Risk Assessment Methodology: docs/risk_assessment_methodology.md
- API Management Guide: docs/api_management_guide.md
- Data Sources Analysis: docs/data_sources_comprehensive_analysis.md
- Temporal Framework: docs/temporal_framework_usage_strategy.md

## Version History

Version 2.5 - Dam Failure, Vector-Borne Disease, and Audit Fixes (March 2026)
- Added Dam Failure as standalone risk domain using real WI DNR Dam Safety Database (~4,100 active dams, weekly cache), USACE NID fallback, NFIP flood zone overlap, and estimated % population in inundation zones
- Added Vector-Borne Disease as standalone risk domain covering Lyme disease, West Nile Virus, Anaplasmosis with climate-adjusted seasonal exposure
- Updated PHRAT from 5 to 7 primary domains with rebalanced weights
- Fixed debug=True hardcoded in main.py (now uses FLASK_DEBUG env var)
- Removed unused Chart.js CDN dependency
- Added database indexes on DataQualityEvent and Feedback tables
- Added request timeouts on all web scraper HTTP calls
- Replaced silent exception swallowing with logged warnings in data modules

Version 2.4 - Real Data Integration and Performance (February 2026)
- Replaced modeled metrics with real cached data from OpenFEMA APIs and NOAA NCEI Storm Events Database
- EVR framework for all natural hazard types with health impact factors using real event counts and damage data
- Full dashboard context caching for near-instant cached load times
- Data freshness tracking with source-specific staleness detection
- YAML-based county-specific baseline scores with documented proxy indicator rationale
- 29 golden file tests verifying score reproducibility and pipeline determinism
- Optimized gunicorn configuration
- AGPLv3 license

Version 2.3 - Configurable Risk Assessment Framework (September 2025)
- YAML-based risk weight configuration system with jurisdiction-specific overrides
- Advanced Z-score normalization and scaling across all risk domains
- Comprehensive contribution logging and variable analysis for transparency
- Kaiser Permanente HVA-compatible Excel exports for hospital preparedness planning
- Blueprint pattern with modular routes and application factory structure

## PHEP Capabilities Integration

CARA aligns with CDC Public Health Emergency Preparedness Cooperative Agreement 2024-2028.

Foundational Capabilities:
- Community Preparedness
- Emergency Operations Coordination
- Information Sharing
- Responder Safety and Health

Incident-Specific Capabilities:
- Medical Countermeasure Dispensing
- Public Health Surveillance
- Medical Surge
- Nonpharmaceutical Interventions

## Research Context

CARA is a research project developed at Georgetown University to support Wisconsin public health preparedness. Users should verify critical information with authoritative sources before making major operational decisions.

## How to Cite CARA

If you use CARA in academic research, policy analysis, reports, or operational planning documents, please cite it as software.

Recommended citation (APA-style):

Niedermeier, J., & Frazier, T. (2026). CARA: Comprehensive Automated Risk Assessment (Version 2.5) [Software]. https://github.com/jdn63/CARA

BibTeX:

```bibtex
@software{cara_2026,
  author = {Niedermeier, Jaime and Frazier, Tim},
  title = {CARA: Comprehensive Automated Risk Assessment},
  year = {2026},
  version = {2.5},
  url = {https://github.com/jdn63/CARA}
}
```

When used in operational or policy contexts, users are encouraged to acknowledge CARA as an open-source public health preparedness risk assessment tool developed for jurisdiction-level strategic planning.

CARA is intended to support preparedness planning, risk awareness, and policy analysis. It should not be used as the sole basis for emergency response or enforcement decisions without corroborating authoritative sources. All data is pre-cached by scheduled background jobs; scores reflect the most recent cache refresh, not live conditions.

## Support

- Issues: Create a GitHub issue with detailed description
- Documentation: Check the docs/ directory
- Community: Join our discussions for best practices sharing

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the LICENSE file for details. This ensures that CARA remains free and open-source, and that any modifications or network deployments must also share their source code.

## Acknowledgments

- Wisconsin Department of Health Services for surveillance data and guidance
- CDC for Public Health Emergency Preparedness framework
- FEMA for natural hazard risk indices
- Georgetown University for research support and development
- Wisconsin public health community for feedback and testing
