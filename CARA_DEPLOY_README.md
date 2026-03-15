# CARA - Comprehensive Automated Risk Assessment

A Flask-based web application for Wisconsin public health departments providing multi-domain risk scoring, real-time data integration, and actionable preparedness guidance.

**Version**: 2.5  
**Developer**: Jaime Niedermeier, PHEP Coordinator at Wisconsin Department of Health Services  
**Affiliation**: Georgetown University Graduate Research Project

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Requirements](#requirements)
5. [Local Setup](#local-setup)
6. [Render.com Deployment](#rendercom-deployment)
7. [Environment Variables](#environment-variables)
8. [Data Files](#data-files)
9. [API Endpoints](#api-endpoints)
10. [License](#license)

---

## Overview

CARA provides comprehensive risk assessment capabilities for 95 Wisconsin jurisdictions:
- 72 County Health Departments
- 12 City/Municipal Health Departments
- 11 Tribal Nations

The platform uses a multi-domain risk scoring system with transparent, documented methodology.

---

## Features

- **Multi-Domain Risk Assessment**: Natural hazards, health metrics, active shooter, extreme heat, and cybersecurity
- **HERC Regional Dashboards**: Aggregated risk data for 7 Healthcare Emergency Readiness Coalition regions
- **GIS Export**: Export risk data as CSV, GeoJSON, and shapefiles for ArcGIS/QGIS
- **Kaiser Permanente HVA Export**: Compatible Excel reports for HERC regions
- **Interactive Maps**: Folium-based geospatial visualizations
- **Strategic Planning Mode**: Long-term risk assessment with adjusted temporal weights
- **Real-time Data Integration**: Air quality, weather alerts, disease surveillance

---

## Project Structure

```
cara/
    main.py                     Application entry point
    core.py                     Flask app factory (create_app)
    models.py                   SQLAlchemy database models
    render.yaml                 Render.com deployment config
    requirements.txt            Python dependencies
    .env.example                Environment variable template

    routes/                     Flask blueprints
        __init__.py
        public.py               Home, methodology, docs
        dashboard.py            Main dashboard routes
        api.py                  REST API endpoints
        herc.py                 HERC regional dashboards
        gis_export.py           GIS export functionality

    templates/                  Jinja2 HTML templates
        base.html
        index.html
        dashboard.html
        methodology.html
        components/             Reusable components
        docs/                   Documentation pages
        errors/                 Error pages

    static/                     Static assets
        css/
        js/
        images/

    utils/                      Utility modules (~50 files)
        main_risk_calculator.py
        herc_risk_aggregator.py
        data_processor.py
        config_manager.py
        ... (many more)

    config/                     Configuration files
        risk_weights.yaml       Risk domain weights

    data/                       Data files
        census/                 Demographics CSV files
        herc/                   HERC region definitions
        tribal/                 Tribal boundary GeoJSON
        nces/                   NCES school safety data (upload separately)
        wi_herc_regions.geojson

    tests/                      Test suite
        conftest.py
        test_api.py
        test_basic.py

    docs/                       Documentation
        deployment_guide.md
        risk_assessment_methodology.md
        data_dictionary.md
```

---

## Requirements

- **Python**: 3.11+
- **Database**: PostgreSQL 14+
- **Memory**: 512MB minimum (1GB recommended)

---

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/cara.git
cd cara
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
createdb cara
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 6. Run the Application

```bash
# Development mode
python main.py

# Production mode with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 main:app
```

### 7. Access the Application

Open http://localhost:5000 in your browser.

---

## Render.com Deployment

### Option 1: Deploy from GitHub (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New", then "Blueprint"
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and configure:
   - PostgreSQL database
   - Web service with gunicorn
   - Environment variables

### Option 2: Manual Deployment

1. Create a new PostgreSQL database on Render
2. Create a new Web Service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 main:app`
3. Add environment variables from `.env.example`
4. Connect your GitHub repo for auto-deploy

### Post-Deployment Steps

1. Upload NCES data files to `data/nces/` directory (if needed)
2. Verify health check at `/api/health`
3. Test main dashboard functionality

---

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `SESSION_SECRET` | Flask session encryption key |
| `DATABASE_URL` | PostgreSQL connection string |

### Optional API Keys

| Variable | Description | Purpose |
|----------|-------------|---------|
| `AIRNOW_API_KEY` | AirNow API | Real-time air quality data |
| `OPENWEATHERMAP_API_KEY` | OpenWeatherMap | Weather alerts |
| `FEMA_RAPT_API_KEY` | FEMA RAPT | Risk assessment data |
| `CENSUS_API_KEY` | Census Bureau | Demographic data |
| `SENTRY_DSN` | Sentry | Error monitoring |

---

## Data Files

### Included in ZIP

- `data/census/wisconsin_demographics.csv` - Population and age data
- `data/census/wisconsin_housing_data.csv` - Housing vulnerability data
- `data/herc/herc_regions.json` - HERC region definitions
- `data/tribal/wisconsin_tribal_boundaries_filtered.geojson` - Tribal boundaries
- `data/gva_reports/` - Gun Violence Archive data
- `config/risk_weights.yaml` - Risk calculation weights

### Upload Separately (Large Files)

The following files are NOT included due to size. Download and upload to `data/nces/`:

- `pu_ssocs20.dta` - NCES School Survey on Crime and Safety (Stata format)
- `pu_ssocs20.sas7bdat` - NCES data (SAS format)
- Other NCES supporting files

**Download from**: [NCES Data Lab](https://nces.ed.gov/datalab/)

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/dashboard/<id>` | GET | Jurisdiction dashboard |
| `/methodology` | GET | Risk methodology documentation |
| `/herc-dashboard/<region>` | GET | HERC regional dashboard |
| `/api/health` | GET | Health check endpoint |
| `/api/gis/export` | POST | GIS data export |

---

## Risk Domains

CARA assesses risk across 7 primary domains aggregated via the PHRAT quadratic mean formula, plus 2 supplementary domains reported separately.

| Domain | Weight | Description |
|--------|--------|-------------|
| Natural Hazards | 28% | NOAA storm events, OpenFEMA claims (EVR framework) |
| Active Shooter | 18% | NCES school safety data, Gun Violence Archive |
| Health Metrics | 17% | Disease surveillance, vaccination rates |
| Air Quality | 12% | EPA AirNow, SVI-adjusted environmental health |
| Extreme Heat | 11% | Heat vulnerability, NWS forecasts |
| Dam Failure | 7% | WI DNR Dam Safety Database, NFIP flood zone overlap |
| Vector-Borne Disease | 7% | Lyme, West Nile Virus (WI DHS EPHT surveillance) |
| Cybersecurity | Supplementary | Infrastructure cyber threats (proxy indicators) |
| Utilities Risk | Supplementary | Electrical, water/sewer, supply chain (proxy indicators) |

---

## Temporal Framework (Strategic Planning Mode)

| Component | Weight | Description |
|-----------|--------|-------------|
| Baseline | 60% | Historical averages |
| Seasonal | 25% | Seasonal patterns |
| Trend | 15% | Long-term trends |
| Acute | 0% | Excluded for strategic planning |

---

## License

This tool was developed by Jaime Niedermeier, PHEP Coordinator at the Wisconsin Department of Health Services, in her capacity as a graduate student at Georgetown University. 

The CARA tool is not affiliated with, nor a reflection of or recommendation by, the Wisconsin Department of Health Services.

---

## Support

For questions or issues, please open a GitHub issue or contact the developer.
