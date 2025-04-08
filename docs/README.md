# Air Quality Analysis - Beaumont

This project analyzes air quality data from monitoring stations in Beaumont, Texas. It processes and visualizes various air quality compounds to identify patterns and trends.

## Project Structure

```
.
├── src/                           # Source code
│   └── air_quality_analysis.py    # Main analysis script
├── data/                          # Data files
│   ├── air_quality_data_with_compounds.csv  # Input data
│   └── detailed_statistics.csv    # Additional statistics
├── docs/                          # Documentation
│   ├── README.md                  # This file
│   └── LICENSE                    # License information
├── plots/                         # Generated visualizations
│   ├── {site_name}_distributions.png
│   ├── {site_name}_hourly_patterns.png
│   ├── {site_name}_weekly_patterns.png
│   ├── {site_name}_monthly_trends.png
│   └── {site_name}_correlation.png
└── requirements.txt               # Python dependencies
```

## Features

The analysis script generates five types of visualizations for each monitoring station:

1. **Distribution Plots**
   - Box plots showing the distribution of concentrations for each compound
   - Helps identify outliers and concentration ranges
   - File format: `plots/{site_name}_distributions.png`

2. **Hourly Patterns**
   - Line charts showing how concentrations vary throughout the day
   - Useful for identifying daily patterns and peak hours
   - File format: `plots/{site_name}_hourly_patterns.png`

3. **Weekly Patterns**
   - Line charts showing concentration variations by day of the week
   - Helps identify weekday vs weekend patterns
   - File format: `plots/{site_name}_weekly_patterns.png`

4. **Monthly Trends**
   - Line charts showing seasonal variations in concentrations
   - Useful for identifying seasonal patterns
   - File format: `plots/{site_name}_monthly_trends.png`

5. **Correlation Heatmap**
   - Heatmap showing relationships between different compounds
   - Helps identify which compounds tend to vary together
   - File format: `plots/{site_name}_correlation.png`

## Data Processing

The script performs the following data processing steps:

1. Converts date and time to datetime format
2. Extracts temporal features (hour, month, day of week)
3. Limits concentration values to 200 for better visualization
4. Handles invalid dates and missing values
5. Groups data by monitoring station

## Requirements

- Python 3.6+
- Required packages:
  - pandas
  - matplotlib
  - seaborn
  - numpy

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure the input data file is in the `data` directory
2. Run the analysis script from the project root:
```bash
python src/air_quality_analysis.py
```
3. Check the `plots` directory for generated visualizations

## Monitoring Stations

The analysis includes data from the following monitoring stations:
- Beaumont Downtown
- Nederland 17th Street

## Notes

- All concentration values are limited to 200 for better visualization
- The script handles missing values and invalid dates
- Visualizations are saved in high resolution (300 DPI)
- Each plot includes proper labels, titles, and legends

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.