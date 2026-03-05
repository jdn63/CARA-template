# Wisconsin Geospatial Health and Emergency Preparedness Risk Assessment Tool
## Comprehensive Methodology Documentation

## 1. Overview
This document provides a detailed explanation of the risk assessment methodology, data sources, calculations, and limitations of the Wisconsin Geospatial Health and Emergency Preparedness Risk Assessment Tool.

### 1.1 Scope
The tool covers all Wisconsin counties with detailed risk assessments for 95 unique public health departments (101 total jurisdiction entries including multi-county secondary mappings). Jurisdictions include:
- 84 local health departments
- 11 federally-recognized tribal nations
- Organized into 7 Healthcare Emergency Readiness Coalition (HERC) regions

## 2. Data Sources and Integration

### 2.1 Real-Time/Active Data Sources
1. **US Census Bureau American Community Survey**
   - Source: Census Bureau ACS 5-Year Estimates API
   - Data Retrieved: 
     - Mobile home counts by county (B25024_010E)
     - Total housing units by county (B25024_001E)
   - Update Frequency: Annual updates from latest ACS release
   - Integration Method: Direct API calls with error handling
   - Data Quality: 
     - 90% confidence interval
     - County-level granularity
     - Fallback to previous year's data if API unavailable

2. **OpenFEMA API**
   - Source: FEMA's Open Data API
   - Endpoint: `https://www.fema.gov/api/open/v1/publicAssistanceFundedProjectsDetails`
   - Data Retrieved: Correctional facility locations, types, and project details
   - Update Frequency: Real-time API calls
   - Integration Status: Active

3. **Wisconsin DHS Data**
   - Source: Wisconsin Department of Health Services
   - Data Retrieved: 
     - ILI (Influenza-like Illness) activity
     - COVID-19 metrics
     - RSV activity
     - Vaccination rates
   - Update Frequency: Weekly updates
   - Integration Status: Active

4. **FEMA National Risk Index (NRI)**
   - Source: FEMA National Risk Index dataset
   - Data Retrieved:
     - Census tract level natural hazards risk scores
     - Building exposure data
   - Update Frequency: Quarterly updates
   - Integration Status: Active

### 2.2 Representative/Placeholder Data (Currently Not Real-Time)
1. **Cybersecurity Risk Data**
   - Current Implementation: Representative data based on county characteristics
   - Future Sources (Planned for Q3 2025): 
     - HHS Breach Portal
     - FBI IC3 Report
     - CISA Known Exploited Vulnerabilities

2. **Active Shooter Risk Assessment**
   - Current Implementation: Population-based estimates
   - Future Integration (Planned for Q4 2025):
     - Law enforcement incident data
     - Emergency response patterns
     - Historical event analysis

3. **Emergency Response Capabilities**
   - Current Implementation: Regional averages
   - Future Integration (Planned for Q3 2025):
     - Real-time emergency services API
     - Response time tracking
     - Resource availability monitoring

## 3. Risk Calculation Methodology

### 3.1 Mobile Home Impact on Tornado Risk
```python
# Using real Census data
mobile_home_percentage = census_mobile_homes / total_housing_units
mobile_home_factor = min(1.0, mobile_home_percentage * 5)
adjusted_tornado_risk = min(1.0, base_tornado_risk * (1 + mobile_home_factor))
```

#### Flood Risk
```python
base_flood_risk = nri_data['flood_risk'] / 100  # Convert to 0-1 scale
final_flood_risk = min(1.0, base_flood_risk * facility_multiplier)
```

#### Tornado Risk
```python
base_tornado_risk = nri_data['tornado_risk'] / 100
#mobile_home_factor = min(1.0, mobile_home_percentage * 5)
#adjusted_tornado_risk = min(1.0, base_tornado_risk * (1 + mobile_home_factor))
#final_tornado_risk = min(1.0, adjusted_tornado_risk * facility_multiplier)
```

#### Winter Storm Risk
```python
base_winter_risk = nri_data['winter_risk'] / 100
final_winter_risk = min(1.0, base_winter_risk * facility_multiplier)
```

### 3.2 Correctional Facility Impact
Facility weights by type:
- State Prison: 1.0 (highest risk weight)
- County Jail: 0.8 (medium-high risk)
- Juvenile Detention: 0.6 (medium risk)
- Treatment Center: 0.4 (medium-low risk)

Facility impact calculation:
```python
facility_impact = sum(weights[facility.type] for facility in facilities)
facility_multiplier = 1 + min(0.2, facility_impact * 0.05)  # Max 20% increase
```

### 3.3 Health Risk Calculation
```python
health_risk_score = (
    ili_activity * 0.3 +
    covid_activity * 0.3 +
    rsv_activity * 0.2 +
    vaccination_rate * 0.2
)
```

### 3.4 Total Risk Score
Weights for different risk components:
- Natural Hazards: 35%
- Health Metrics: 20%
- Active Shooter: 15%
- Extreme Heat: 15%
- Cybersecurity: 15%

```python
total_risk_score = (
    natural_hazard_score * 0.35 +
    health_risk_score * 0.20 +
    active_shooter_risk * 0.15 +
    extreme_heat_risk * 0.15 +
    cybersecurity_risk * 0.15
)
```

## 4. Current Limitations

### 4.1 Data Source Limitations
1. **Census Data Timing**
   - Annual updates may not reflect very recent changes
   - ACS estimates have statistical margins of error
   - Rural areas may have higher uncertainty

2. **API Reliability**
   - Census API may have occasional downtime
   - OpenFEMA API limited to facilities with past disaster declarations
   - DHS data may have reporting delays

3. **Correctional Facility Data**
   - OpenFEMA API limited to facilities with past disaster declarations
   - May miss newer facilities or those without FEMA interaction
   - Facility capacity data not currently integrated

4. **Health Metrics**
   - Limited to publicly available DHS data
   - Some metrics may have reporting delays
   - Rural areas may have less granular data


### 4.2 Methodological Limitations
1. **Risk Weighting**
   - Weights are predetermined and may not reflect local variations
   - Linear scaling may oversimplify complex risk relationships
   - Facility impact cap (20%) may not suit all scenarios

2. **Geographic Resolution**
   - Some data only available at county level
   - Census tract level data may not capture neighborhood variations
   - Tribal areas may have different risk patterns not fully captured

3. **Temporal Limitations**
   - Historical trends limited by data availability
   - Seasonal variations not fully incorporated
   - Future projections based on simple trend analysis

## 5. Data Validation and Quality Assurance

### 5.1 Census Data Validation
- Automated checks for data completeness
- Comparison with previous year's values
- Statistical outlier detection
- Fallback to representative data if API fails

### 5.2 General Data Quality Measures
1. **Data Completeness Checks:** Automated checks to ensure all necessary data fields are populated.
2. **Data Consistency Checks:** Comparisons across data sources to identify inconsistencies.
3. **Outlier Detection:** Identification and investigation of extreme values that deviate significantly from the norm.
4. **Error Handling:** Mechanisms to gracefully manage API failures or data anomalies.
5. **Data Documentation:** Clear and thorough documentation to describe data sources, processing steps, and potential limitations.

## 6. Version Control and Updates
- Current Version: 1.1.0
- Last Updated: April 4, 2025
- Next Scheduled Review: September 30, 2025

### 6.1 Recent Updates
- Version 1.1.0 (April 4, 2025)
  - Added coverage for all 95 Wisconsin public health agencies including 84 public health departments and 11 tribal health centers
  - Improved data scraping for Wisconsin DHS portal with specific handling for tribal health centers
  - Enhanced jurisdiction mapping for all counties including areas with multiple jurisdictions
  - Updated documentation to accurately reflect all covered health entities
  
- Version 1.0.0 (March 24, 2025)
  - Initial release with 12 core jurisdictions
  - Base implementation of risk calculation methodology
  - Integration with Census, DHS, and FEMA data sources

## 7. Contact and Support
For questions about this methodology or to suggest improvements, please contact the development team.