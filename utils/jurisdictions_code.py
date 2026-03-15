"""
CARA Template - Public Health Jurisdictions

TEMPLATE FILE: Replace these example jurisdictions with your actual
public health department jurisdictions.

Each entry requires:
  - 'id': A unique identifier (string)
  - 'name': The full name of the health department or jurisdiction
  - 'county': The county (or equivalent administrative area) served
  - 'primary': True for canonical entries (shown in dropdowns),
               False for secondary entries in multi-county departments
               (used in GIS/regional aggregation)

Instructions:
  1. Replace the example entries below with your jurisdiction's health departments
  2. Set primary=True for each department's main entry
  3. If a department serves multiple counties, create one primary=True entry
     and additional primary=False entries for each additional county
  4. Update the totals in this docstring to match your jurisdiction

Total: 5 example entries (4 unique health departments + 1 secondary multi-county entry)
"""

jurisdictions = [
    {
        'id': '1',
        'name': 'Example County A Health Department',
        'county': 'County A',
        'primary': True
    },
    {
        'id': '2',
        'name': 'Example County B Public Health Division',
        'county': 'County B',
        'primary': True
    },
    {
        'id': '3',
        'name': 'Example County C Health & Human Services',
        'county': 'County C',
        'primary': True
    },
    {
        'id': '4',
        'name': 'Example Counties D-E Regional Health Department',
        'county': 'County D',
        'primary': True
    },
    {
        'id': '5',
        'name': 'Example Counties D-E Regional Health Department',
        'county': 'County E',
        'primary': False
    },
]
