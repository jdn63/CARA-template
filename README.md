# CARA - Comprehensive Automated Risk Assessment

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A comprehensive, open-source geospatial health and emergency preparedness risk assessment platform. CARA is designed as a **template** that any public health jurisdiction can adapt and deploy for their own multi-domain risk scoring, data integration, and preparedness planning needs.

## What is CARA?

CARA provides a turnkey risk assessment web application for public health departments and emergency management agencies. It integrates data from authoritative federal, state, and local sources to produce actionable, jurisdiction-level risk scores aligned with CDC Public Health Emergency Preparedness (PHEP) capabilities.

This repository is the **template version** of CARA. It contains placeholder jurisdictions and example data so you can quickly customize it for your own state, region, or territory.

### Key Features

- **Multi-Domain Risk Assessment**: 5 primary domains (natural hazards, infectious disease, active shooter, extreme heat, air quality) plus supplementary assessments (cybersecurity, utilities)
- **Real Data Integration**: Pre-cached data from OpenFEMA APIs, NOAA Storm Events Database, EPA AirNow, and local Census/FEMA NRI files
- **Performance-Optimized**: Full dashboard context caching for near-instant load times after initial cache build
- **Strategic Planning Mode**: Long-term risk assessment optimized for annual preparedness planning cycles
- **PHEP Alignment**: Full integration with CDC Public Health Emergency Preparedness capabilities
- **Automated Action Plans**: Customized preparedness recommendations with implementation timelines
- **Interactive Visualization**: Geospatial mapping, risk distribution charts, and trend analysis
- **GIS Export**: CSV, GeoJSON, and Shapefile exports for ArcGIS/QGIS
- **HVA Export**: Kaiser Permanente HVA-compatible Excel reports for hospital preparedness planning

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL with PostGIS extension
- API keys for optional data sources (see Configuration)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/cara.git
   cd cara
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/cara_db"
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open** `http://localhost:5000` in your browser

The template ships with 5 example jurisdictions so you can explore the full interface immediately.

### Adapting CARA for Your Jurisdiction

CARA is designed for adaptation. To customize it for your jurisdiction:

1. **Replace jurisdiction data** in `utils/jurisdictions_code.py` with your real jurisdictions
2. **Update data files** in `data/census/`, `data/svi/`, and `data/herc/` (or your equivalent regional grouping)
3. **Configure risk baselines** in `config/county_baselines.yaml`
4. **Customize branding** in templates (replace `[Your Jurisdiction]` placeholders)
5. **Connect your data sources** by modifying the utility modules marked `JURISDICTION-SPECIFIC`

For detailed adaptation guidance, see:
- **[Adaptation Workshop Guide](docs/CARA_Adaptation_Workshop_Guide.md)** -- step-by-step workshop for adapting CARA
- **[Replit Workshop Guide](docs/CARA_Replit_Workshop_Guide.md)** -- deploying on Replit
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** -- production deployment instructions

## Architecture

### Backend
- **Framework**: Flask (Python) with Blueprint architecture and application factory pattern
- **Database**: PostgreSQL with PostGIS extension for geospatial data
- **Data Processing**: Pandas, NumPy, GeoPandas for data manipulation
- **Scheduling**: APScheduler for automated data refreshes
- **APIs**: RESTful integration with multiple government data sources

### Frontend
- **Templates**: Jinja2 with Bootstrap 5 responsive design
- **Visualization**: Chart.js for interactive charts, Folium for mapping
- **Accessibility**: WCAG 2.1 AA compliant design with screen reader support
- **Performance**: Lazy loading, caching, and optimized asset delivery

## Risk Assessment Framework

CARA employs a multi-dimensional risk assessment methodology using 5 primary risk domains:

| Domain | Weight | Description |
|--------|--------|-------------|
| **Natural Hazards** | 33% | Flood, tornado, winter storm, thunderstorm (EVR framework with real NOAA/OpenFEMA data) |
| **Health Metrics** | 20% | Infectious disease surveillance and vaccination rates |
| **Active Shooter** | 20% | Community violence risk assessment |
| **Extreme Heat** | 13% | Heat vulnerability and climate-adjusted risk |
| **Air Quality** | 14% | Environmental health and AQI assessment |
| **Cybersecurity** | Supplementary | Critical infrastructure cyber threats (proxy indicators) |
| **Utilities Risk** | Supplementary | Electrical, water/sewer, supply chain, fuel shortage (proxy indicators) |

The 5 primary domains are aggregated using the **PHRAT quadratic mean formula** (p=2), which appropriately emphasizes higher-risk domains rather than averaging them away.

### Temporal Framework (BSTA)

- **Baseline (60%)**: Long-term structural risk factors
- **Seasonal (25%)**: Predictable cyclical variations
- **Trend (15%)**: Medium-term directional changes
- **Acute (0%)**: Short-term event-driven spikes (Strategic Planning Mode)

### Social Vulnerability Integration

All risk calculations incorporate CDC Social Vulnerability Index (SVI) factors:
- Socioeconomic status
- Household composition & disability
- Minority status & language
- Housing type & transportation

## Configuration

### Required Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@localhost/cara_db
SESSION_SECRET=your_secure_session_secret
```

### Optional API Keys

```bash
AIRNOW_API_KEY=your_airnow_api_key        # Air quality data
OPENWEATHER_API_KEY=your_openweather_key   # Weather data
```

### Data Sources

CARA integrates with multiple authoritative data sources, all pre-fetched by scheduled background jobs and cached locally:

- **OpenFEMA APIs (keyless)**: Disaster Declarations, NFIP Claims, Hazard Mitigation Projects
- **NOAA NCEI Storm Events Database**: Bulk CSV downloads of storm events
- **CDC**: Social Vulnerability Index and PHEP guidelines
- **FEMA NRI**: National Risk Index data (local CSV files)
- **EPA AirNow**: Air quality monitoring (requires API key)
- **NOAA/NWS**: Heat forecasting and weather alerts
- **Census Bureau**: Demographic and housing data (local CSV files)

## Project Structure

```
cara/
├── main.py                 # Application entry point
├── core.py                 # Flask app factory
├── models.py               # SQLAlchemy database models
├── routes/                 # Flask blueprints
│   ├── api.py              # REST API endpoints
│   ├── dashboard.py        # Risk dashboard views
│   ├── herc.py             # Regional dashboard views
│   ├── gis_export.py       # GIS data export
│   └── public.py           # Public pages
├── utils/                  # Business logic and data processing
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, images
├── data/                   # Local data files
├── config/                 # YAML configuration
├── tests/                  # Test suite
└── docs/                   # Documentation and workshop guides
```

## Documentation

- **[Adaptation Workshop Guide](docs/CARA_Adaptation_Workshop_Guide.md)** -- step-by-step adaptation instructions
- **[Replit Workshop Guide](docs/CARA_Replit_Workshop_Guide.md)** -- deploying on Replit
- **[Risk Assessment Methodology](docs/risk_assessment_methodology.md)** -- detailed calculation methods
- **[API Management Guide](docs/api_management_guide.md)** -- API integration best practices
- **[Data Sources Analysis](docs/data_sources_comprehensive_analysis.md)** -- complete data source documentation
- **[Temporal Framework](docs/temporal_framework_usage_strategy.md)** -- strategic planning implementation
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** -- production deployment

## How to Cite CARA

If you use CARA in academic research, policy analysis, reports, or operational planning documents, please cite it as software.

**Recommended citation (APA-style):**

> Niedermeier, J. (2026). *CARA: Comprehensive Automated Risk Assessment* (Version 2.4) [Software]. https://github.com/jdn63/CARA

**BibTeX:**

```bibtex
@software{cara_2026,
  author  = {Niedermeier, Jaime},
  title   = {CARA: Comprehensive Automated Risk Assessment},
  year    = {2026},
  version = {2.4},
  url     = {https://github.com/jdn63/CARA}
}
```

## Contributing

We welcome contributions from the public health and emergency management community! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** -- see the [LICENSE](LICENSE) file for details. This ensures that CARA remains free and open-source, and that any modifications or network deployments must also share their source code.

## Acknowledgments

- **CDC** for the Public Health Emergency Preparedness framework
- **FEMA** for natural hazard risk indices and OpenFEMA APIs
- **Georgetown University** for research support and development
- **Public health practitioners** who provided feedback and testing

---

**Built for Public Health Preparedness**
