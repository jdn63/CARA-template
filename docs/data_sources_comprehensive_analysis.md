# CARA Application - Comprehensive Data Sources Analysis

## Overview

This document provides a complete mapping of all data sources used in the CARA application across all risk types and calculations. Understanding where data comes from is crucial for transparency and validation.

## Data Source Categories

### 🟢 **Strategic Data Sources** (Enhanced for Planning)
These are primary data sources optimized for strategic planning:

1. **Local Census Data Files** ✅ 
   - **Service**: County-specific CSV files with Wisconsin demographic data
   - **Used For**: Mobile home percentages, elderly population, total population by county
   - **Files**: `data/census/wisconsin_housing_data.csv`, `data/census/wisconsin_demographics.csv`
   - **Benefits**: 100% offline capability, county-specific accuracy, no API failures
   - **Refresh**: Manual updates with authoritative data

2. **Strategic Planning Data Cache** ✅
   - **Service**: Extended cache periods for annual planning cycles
   - **Used For**: Climate projections, historical trends, baseline risk assessments
   - **Cache Duration**: 30-180 days depending on data stability
   - **Benefits**: Consistent strategic planning data, reduced API dependencies

3. **FBI Crime Data API** ✅
   - **Service**: FBI Uniform Crime Reporting (UCR) data
   - **Used For**: Crime statistics for active shooter risk assessment
   - **URL**: `https://api.fbi.gov/wanted/v1/`
   - **Validation**: API key validated successfully
   - **Refresh**: Every 90 days

### 🟡 **Static/Local Data Sources**
These are pre-loaded datasets stored locally in the application:

4. **FEMA National Risk Index (NRI)** 📁
   - **Source**: Downloaded CSV from FEMA
   - **File**: `attached_assets/NRI_Table_CensusTracts_Wisconsin_FloodTornadoWinterOnly.csv`
   - **Used For**: Natural hazard risk scores (flooding, tornado, winter storm)
   - **Last Updated**: Static file - needs manual updates

5. **Gun Violence Archive (GVA)** 📁
   - **Source**: Downloaded CSV from gunviolencearchive.org
   - **File**: `attached_assets/GunViolenceArchive 2023 mass shootings data.csv`
   - **Used For**: Historical gun violence incidents for active shooter risk
   - **Status**: Static file - needs manual updates

6. **CDC Social Vulnerability Index (SVI)** 📁
   - **Source**: CDC/ATSDR SVI data
   - **Location**: `data/svi/wisconsin_svi_data.json`
   - **Used For**: Social vulnerability factors
   - **Status**: Static with placeholder data - needs API integration

7. **NCES School Safety Data** 📁
   - **Source**: National Center for Education Statistics SSOCS survey
   - **File**: `attached_assets/SSOCS 2019_2020 data.zip`
   - **Used For**: School safety indicators in active shooter risk
   - **Status**: Static 2019-2020 data

### 🔴 **Simulated/Placeholder Data Sources**
These modules currently use simulated data:

8. **Wisconsin DHS Health Data** ✅
   - **Module**: `utils/dhs_data.py` with `utils/web_scraper.py`
   - **Source**: Real-time web scraping of Wisconsin DHS respiratory illness pages
   - **Gets**: Disease surveillance, activity levels, emergency department data
   - **Status**: **SUCCESSFULLY INTEGRATED** - Live data from official DHS pages

9. **Disease Surveillance Data** 🎲
   - **Module**: `utils/disease_surveillance.py`
   - **Should Get**: Flu, COVID-19, RSV activity levels
   - **Currently**: Simulated seasonal patterns
   - **Status**: **NEEDS REAL DATA SOURCE**

10. **Climate Projections** 🎲
    - **Module**: `utils/climate_adjusted_risk.py`
    - **Should Get**: Climate change projections, seasonal forecasts
    - **Currently**: Default trend factors and simulated data
    - **Status**: **NEEDS NOAA/CLIMATE API**

11. **Utilities Risk Data** 🎲
    - **Module**: `utils/utilities_risk.py`
    - **Should Get**: Power outages, infrastructure disruptions
    - **Currently**: Statistical models with placeholder data
    - **Status**: **NEEDS UTILITY COMPANY APIS**

## Risk Domain Data Source Breakdown

### **Natural Hazards Risk**
- ✅ **FEMA NRI**: Flood, tornado, winter storm baseline risk
- ✅ **Strategic Planning Cache**: Long-term climate data with 30-180 day cache periods
- 🔴 **Climate Projections**: Trend adjustments (currently simulated)

### **Active Shooter Risk**
- ✅ **Gun Violence Archive**: Historical incident data (static file)
- ✅ **FBI Crime Data API**: Crime statistics
- ✅ **Local Census Files**: County-specific demographics from CSV files (mobile homes, elderly population)
- 📁 **NCES SSOCS**: School safety data (2019-2020)
- 📁 **CDC SVI**: Social vulnerability factors

### **Infectious Disease Risk**
- 🔴 **Wisconsin DHS**: Disease surveillance (simulated)
- 🔴 **Vaccination Data**: Coverage rates (simulated)
- 🔴 **CDC FluView**: Influenza activity (not integrated)

### **Cybersecurity Risk**
- 🔴 **HHS Breach Portal**: Healthcare breaches (simulated)
- 🔴 **CISA KEV**: Known exploited vulnerabilities (simulated)
- 🔴 **FBI IC3**: Cybercrime reports (simulated)

### **Utilities/Infrastructure Risk**
- 🔴 **Power Company APIs**: Outage data (simulated)
- 🔴 **Supply Chain Disruptions**: Transportation/logistics (simulated)
- 🔴 **Fuel Shortage Data**: Regional fuel availability (simulated)

### **Extreme Heat Risk**
- ✅ **Strategic Climate Data**: Historical baseline with long-term projections (30-day cache)
- 🔴 **Wisconsin DHS ED Visits**: Heat-related emergency visits (simulated)
- 🔴 **Cooling Center Data**: Availability and capacity (simulated)

## Data Refresh Schedule

| Data Source | Refresh Interval | Last Updated | Status |
|-------------|------------------|--------------|---------|
| Strategic Planning Data | 30-90 days | Cached | ✅ Active |
| Disease Surveillance | 7-30 days | Cached API | ✅ Active |
| Air Quality Data | 1-30 days | Cached API | ✅ Active |
| FEMA NRI Data | 180 days | Cached | ✅ Active |
| SVI Data | 90 days | Cached | ✅ Active |
| Crime Statistics | 30-90 days | Cached API | ✅ Active |
| Census Data | Local Files | No refresh needed | ✅ Active |
| Climate Projections | 365 days | Simulated | 🔴 Needs API |

## Critical Data Gaps

### **Completed Strategic Enhancements** ✅
1. **Local Census Data**: County-specific demographics with no API dependencies
2. **Strategic Cache System**: Extended cache periods optimized for annual planning
3. **Enhanced Reliability**: Offline capability with graceful API fallbacks
4. **Data Accuracy**: County-level precision vs regional estimates

### **Medium Priority** (Enhances Accuracy)
1. **Utility Company APIs**: Real power outage and infrastructure data
2. **HHS Breach Portal API**: Healthcare cybersecurity incidents
3. **CISA API**: Known exploited vulnerabilities
4. **Transportation APIs**: Supply chain disruption data

### **Low Priority** (Nice to Have)
1. **Local Emergency Management APIs**: County-specific preparedness data
2. **Hospital APIs**: Emergency department capacity and usage
3. **Educational APIs**: Real-time school safety and enrollment data

## Recommendations for Data Source Improvements

### **Immediate Actions**
1. **Integrate CDC SVI API** - Replace placeholder social vulnerability data
2. **Update GVA Data** - Download current year mass shooting data
3. **Add NOAA Climate APIs** - Replace simulated seasonal forecasts

### **Short-term Improvements** (1-3 months)
1. **Wisconsin DHS Integration** - Work with state health department for API access
2. **HHS Breach Portal API** - Add real cybersecurity incident data
3. **CISA Integration** - Connect to known exploited vulnerabilities feed

### **Long-term Enhancements** (3-12 months)
1. **Utility Company Partnerships** - Arrange data sharing agreements
2. **Local Emergency Management Integration** - County-specific preparedness data
3. **Hospital System APIs** - Emergency department utilization data

## Data Quality Assurance

### **Current Validation**
- ✅ API key validation for external services
- ✅ Data type checking and sanitization
- ✅ Geographic boundary validation for Wisconsin

### **Needed Improvements**
- 🔴 Real-time data freshness monitoring
- 🔴 Data source outage detection and alerting
- 🔴 Automated data quality scoring
- 🔴 Source data lineage tracking

## Transparency Notes

**For Public Health Officials**: The application currently uses a mix of real-time APIs, static datasets, and simulated data. Risk scores should be interpreted as analytical estimates rather than definitive assessments, particularly for domains relying on simulated data.

**For Technical Users**: All data source configurations are documented in `data/config/scheduler_config.json`, and individual modules contain detailed information about their data sources and processing methods.

---

**Last Updated**: July 5, 2025  
**Next Review**: Update when new data sources are integrated