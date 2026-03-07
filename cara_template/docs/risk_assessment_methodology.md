# Risk Assessment Methodology

## Data Sources and Risk Calculations

### Real-Time Data Sources
| Data Type | Source | Update Frequency | Data Scale |
|-----------|--------|-----------------|------------|
| Mobile Home Statistics | US Census Bureau ACS API | Annual | County Level |
| Health Metrics | Wisconsin DHS API | Weekly | County Level |
| Natural Hazards Risk | FEMA NRI Dataset | Quarterly | Census Tract Level |

### Representative/Placeholder Data
| Data Type | Current Implementation | Planned Future Source | Update Timeline |
|-----------|----------------------|---------------------|-----------------|
| Cybersecurity Risk | Static county-based metrics | HHS Breach Portal, FBI IC3 Report | Q3 2025 |
| Active Shooter Risk | Population-based estimates | Law enforcement data integration | Q4 2025 |
| Emergency Response Times | Regional averages | Real-time emergency services API | Q3 2025 |


## Risk Calculations

### Natural Hazards (Flood, Tornado, Winter Storm)
```python
risk_score = (nri_base_score / 100) * historical_adjustment_factor
```

### Mobile Home Impact on Tornado Risk
```python
mobile_home_factor = min(1.0, census_mobile_home_percentage * 5)
adjusted_tornado_risk = min(1.0, base_tornado_risk * (1 + mobile_home_factor))
```

### Health Metrics Impact
- Hospital Beds per 1000 residents (weight: 30%)
- Vaccination Rate (weight: 25%)
- Emergency Response Time (weight: 25%)
- Healthcare Facilities Density (weight: 20%)

### Total Risk Score Calculation
```python
total_risk = (
    natural_hazard_score * 0.6 +
    infectious_disease_risk * 0.2 +
    active_shooter_risk * 0.2
)
```

## Risk Level Categories
- Low Risk: < 0.3
- Medium Risk: 0.3 - 0.6
- High Risk: > 0.6

## Data Update Frequency
- Census Mobile Home Data: Updated annually from ACS API
- Natural Hazard Data: Updated quarterly from FEMA NRI
- Health Metrics: Updated weekly from DHS
- Weather Alerts: Real-time updates
- Representative Data: Updated as better sources become available

## Jurisdiction-Specific Adjustments

### Milwaukee City (ID: 41)
- Higher base infectious disease risk (0.4 vs 0.3)
- Higher base active shooter risk (0.2 vs 0.1)
- Enhanced flood risk monitoring

### Other Counties
- Customized risk factors based on:
  * Geographic location
  * Population density
  * Healthcare infrastructure
  * Historical incident patterns

## Data Validation
- Automated outlier detection
- Cross-validation with historical trends
- Quarterly accuracy assessments
- Real-time monitoring of extreme values

## References
1. US Census Bureau American Community Survey API
2. FEMA National Risk Index (NRI) - Wisconsin Dataset
3. Wisconsin Department of Health Services
4. County Health Department Reports
5. National Weather Service Data