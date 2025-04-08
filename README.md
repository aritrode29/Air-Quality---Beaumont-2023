# Air Quality Analysis for Beaumont Area

This project analyzes air quality data from monitoring stations in the Beaumont area, with a focus on compounds associated with refinery operations.

## Data Source

The analysis uses data from two monitoring stations:
- Beaumont Downtown
- Nederland 17th Street

## Compound Categories

The analysis categorizes compounds into three main refinery-related groups:

### 1. Aromatics (Red)
- Benzene
- Toluene
- Xylenes (m/p-Xylene, o-Xylene)
- Ethylbenzene
- Styrene
- Trimethylbenzenes (1,2,3-, 1,2,4-, 1,3,5-)

### 2. Olefins (Teal)
- Ethylene
- Propylene
- 1,3-Butadiene
- Butenes (1-Butene, cis-2-Butene, trans-2-Butene)

### 3. Alkanes (Blue)
- n-Hexane through n-Decane
- Cyclohexane
- Methylcyclohexane

## Visualizations

The analysis generates the following visualizations for each monitoring station:

### 1. Distribution Plots
   - Box plots showing concentration distributions
   - Two versions available:
     - Original version (uniform teal color)
     - Refinery-classified version (color-coded by category)
   - Concentrations limited to 50 µg/m³ for better visualization
   - Larger box sizes for improved visibility

### 2. Hourly Patterns
   - Line charts showing daily concentration variations
   - Two versions available:
     - Original version (uniform teal color)
     - Refinery-classified version (color-coded by category)
   - Solid lines for refinery compounds
   - Dashed lines for other compounds

### 3. Weekly Patterns
   - Concentration variations by day of the week
   - Helps identify weekly operational patterns

### 4. Monthly Trends
   - Seasonal variations in concentrations
   - Useful for identifying seasonal patterns

### 5. Correlation Heatmap
   - Shows relationships between different compounds
   - Helps identify co-occurring pollutants

### 6. Wind Rose Plot
   - Shows wind direction and speed patterns
   - Helps understand pollutant dispersion

### 7. Compound Correlations
   - Detailed correlation matrix for all compounds
   - Focuses on refinery-related compounds

### 8. Concentration Heatmap
   - Daily compound concentrations over time
   - Helps identify pollution events

## Usage

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the analysis:
   ```bash
   python src/air_quality_analysis.py
   ```

3. View generated plots in the `plots` directory:
   - Original plots: `{site_name}_distributions_original.png`, `{site_name}_hourly_patterns_original.png`
   - Refinery-classified plots: `{site_name}_distributions.png`, `{site_name}_hourly_patterns.png`
   - Other plots: `{site_name}_weekly_patterns.png`, `{site_name}_monthly_trends.png`, etc.

## Requirements

- Python 3.8+
- pandas>=2.0.0
- matplotlib>=3.7.0
- seaborn>=0.12.0
- numpy>=1.24.0

## Directory Structure

```
.
├── data/
│   ├── air_quality_data_with_compounds.csv
│   └── detailed_statistics.csv
├── plots/
│   └── [Generated visualization files]
├── src/
│   └── air_quality_analysis.py
├── docs/
│   └── [Documentation files]
└── requirements.txt
```

## Notes

- All concentration values are limited to 50 µg/m³ for better visualization of lower ranges
- Refinery compounds are highlighted in plots using specific colors:
  - Aromatics: Red (#FF6B6B)
  - Olefins: Teal (#4ECDC4)
  - Alkanes: Blue (#45B7D1)
- Non-refinery compounds are shown in gray (#96A5A6)
- The analysis includes error handling for missing data
- Box plots have been enhanced with:
  - Larger box sizes (width=0.7)
  - Higher opacity (0.8)
  - Thicker lines (2pt)
  - Higher resolution output (300 DPI) 