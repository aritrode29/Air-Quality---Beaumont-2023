import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import gc
from datetime import datetime
import sys
import traceback

# Define periods of interest
PERIODS = {
    'Oct_2023': {
        'start': '2023-10-08',
        'end': '2023-10-20',
        'label': 'October 8-20, 2023'
    },
    'Feb_Mar_2023': {
        'start': '2023-02-20',
        'end': '2023-03-15',
        'label': 'February 20 - March 15, 2023'
    }
}

# Define refinery-associated compounds and their categories
REFINERY_COMPOUNDS = {
    # Aromatics (from catalytic reforming and other processes)
    'Benzene': 'Aromatics',
    'Toluene': 'Aromatics',
    'm/p Xylene': 'Aromatics',
    'o-Xylene': 'Aromatics',
    'Ethylbenzene': 'Aromatics',
    'Styrene': 'Aromatics',
    '1,2,3-Trimethylbenzene': 'Aromatics',
    '1,2,4-Trimethylbenzene': 'Aromatics',
    '1,3,5-Trimethylbenzene': 'Aromatics',
    
    # Olefins (from fluid catalytic cracking)
    'Ethylene': 'Olefins',
    'Propylene': 'Olefins',
    '1,3-Butadiene': 'Olefins',
    '1-Butene': 'Olefins',
    'cis-2-Butene': 'Olefins',
    'trans-2-Butene': 'Olefins',
    
    # Alkanes (from various refinery processes)
    'n-Hexane': 'Alkanes',
    'n-Heptane': 'Alkanes',
    'n-Octane': 'Alkanes',
    'n-Nonane': 'Alkanes',
    'n-Decane': 'Alkanes',
    'Cyclohexane': 'Alkanes',
    'Methylcyclohexane': 'Alkanes'
}

# Define colors for each category
CATEGORY_COLORS = {
    'Aromatics': '#FF6B6B',  # Red
    'Olefins': '#4ECDC4',    # Teal
    'Alkanes': '#45B7D1',    # Blue
    'Other': '#96A5A6'       # Gray
}

def get_compound_color(compound):
    """Return the color for a compound based on its category."""
    if compound in REFINERY_COMPOUNDS:
        category = REFINERY_COMPOUNDS[compound]
        return CATEGORY_COLORS[category]
    return CATEGORY_COLORS['Other']

def setup_visualization():
    """Set up visualization parameters."""
    try:
        # Use a basic style that's always available
        plt.style.use('default')

        # Set global plot parameters
        plt.rcParams.update({
            'figure.figsize': (20, 10),
            'font.size': 12,
            'axes.labelsize': 14,
            'axes.titlesize': 16,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'axes.grid': True,
            'grid.alpha': 0.3
        })
        print("Visualization settings configured successfully")
    except Exception as e:
        print(f"Error setting up visualization parameters: {str(e)}")
        raise

def process_data(df):
    """Process the air quality data for analysis."""
    try:
        # Convert date and time to datetime
        df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'], 
                                       format='%Y%m%d %H:%M', errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d', errors='coerce')
        
        # Extract temporal features
        df['Hour'] = df['DateTime'].dt.hour
        df['Month'] = df['DateTime'].dt.month
        df['DayOfWeek'] = df['DateTime'].dt.dayofweek
        
        # Limit concentration values to 15
        df['Value'] = df['Value'].clip(upper=15)
        
        return df
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        raise

def plot_period_comparison(data, site_name, period_name, period_info):
    """Create comprehensive visualizations for a specific period."""
    try:
        # Filter data for the period
        period_data = data[
            (data['DateTime'] >= period_info['start']) & 
            (data['DateTime'] <= period_info['end'])
        ].copy()  # Make a copy to avoid memory issues
        
        if len(period_data) == 0:
            print(f"No data found for {period_info['label']} at {site_name}")
            return
        
        # Create directory for period-specific plots
        period_dir = os.path.join('plots', 'period_analysis', period_name)
        os.makedirs(period_dir, exist_ok=True)
        
        # Split compounds into two groups based on concentration
        compounds = period_data['Compound_Name'].unique()
        low_concentration = []
        high_concentration = []
        
        for compound in compounds:
            max_concentration = period_data[period_data['Compound_Name'] == compound]['Value'].max()
            if max_concentration < 2:
                low_concentration.append(compound)
            else:
                high_concentration.append(compound)
        
        # Process each plot type separately to manage memory
        plot_types = [
            ('timeseries', plot_timeseries),
            ('distributions', plot_distributions),
            ('hourly_patterns', plot_hourly_patterns),
            ('correlations', plot_correlations)
        ]
        
        for plot_name, plot_func in plot_types:
            try:
                print(f"Generating {plot_name} for {site_name} - {period_info['label']}")
                plot_func(period_data, site_name, period_dir, period_info, 
                         low_concentration, high_concentration)
                plt.close('all')  # Close all figures
                gc.collect()  # Force garbage collection
            except Exception as e:
                print(f"Error generating {plot_name} for {site_name}: {str(e)}")
                continue
        
        print(f"Generated plots for {period_info['label']} at {site_name}")
        
    except Exception as e:
        print(f"Error creating plots for {period_info['label']} at {site_name}: {str(e)}")
        raise

def plot_timeseries(data, site_name, period_dir, period_info, low_concentration, high_concentration):
    """Plot time series for both low and high concentration compounds."""
    try:
        # Plot for low concentration compounds
        if low_concentration:
            try:
                plt.figure(figsize=(24, 12))
                low_data = data[data['Compound_Name'].isin(low_concentration)].copy()
                
                if len(low_data) > 0:
                    low_data['Value'] = low_data['Value'] * 1000  # Convert to ng/m³
                    low_data['Value'] = low_data['Value'].clip(upper=250)
                    
                    # Create a color map for the compounds
                    colors = [get_compound_color(compound) for compound in low_concentration]
                    
                    # Plot each compound
                    for compound, color in zip(low_concentration, colors):
                        compound_data = low_data[low_data['Compound_Name'] == compound]
                        if len(compound_data) > 0:
                            plt.plot(compound_data['DateTime'], compound_data['Value'], 
                                   label=compound, color=color, alpha=0.7, linewidth=2)
                    
                    # Add threshold lines
                    plt.axhline(y=250, color='r', linestyle='--', alpha=0.3, label='250 ng/m³ limit')
                    plt.axhline(y=100, color='orange', linestyle='--', alpha=0.3, label='100 ng/m³')
                    plt.axhline(y=50, color='g', linestyle='--', alpha=0.3, label='50 ng/m³')
                    
                    # Format the plot
                    plt.title(f'Time Series of Low Concentration Compounds\n{site_name} - {period_info["label"]}',
                            fontsize=16, pad=20)
                    plt.xlabel('Date and Time', fontsize=14)
                    plt.ylabel('Concentration (ng/m³)', fontsize=14)
                    
                    # Format x-axis
                    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
                    plt.xticks(rotation=45, ha='right')
                    
                    # Add grid
                    plt.grid(True, alpha=0.3)
                    
                    # Adjust legend
                    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                             frameon=True, framealpha=0.9, fontsize=10)
                    
                    # Adjust layout
                    plt.tight_layout()
                    
                    # Save the plot
                    plt.savefig(os.path.join(period_dir, f'{site_name}_timeseries_low.png'),
                              bbox_inches='tight', dpi=300)
                else:
                    print(f"No low concentration data found for {site_name}")
                plt.close()
            except Exception as e:
                print(f"Error plotting low concentration time series for {site_name}: {str(e)}")
                plt.close()
        
        # Plot for high concentration compounds
        if high_concentration:
            try:
                plt.figure(figsize=(24, 12))
                high_data = data[data['Compound_Name'].isin(high_concentration)].copy()
                
                if len(high_data) > 0:
                    # Create a color map for the compounds
                    colors = [get_compound_color(compound) for compound in high_concentration]
                    
                    # Plot each compound
                    for compound, color in zip(high_concentration, colors):
                        compound_data = high_data[high_data['Compound_Name'] == compound]
                        if len(compound_data) > 0:
                            plt.plot(compound_data['DateTime'], compound_data['Value'], 
                                   label=compound, color=color, alpha=0.7, linewidth=2)
                    
                    # Add threshold lines
                    plt.axhline(y=2, color='r', linestyle='--', alpha=0.3, label='2 µg/m³')
                    plt.axhline(y=1, color='orange', linestyle='--', alpha=0.3, label='1 µg/m³')
                    plt.axhline(y=0.5, color='g', linestyle='--', alpha=0.3, label='0.5 µg/m³')
                    
                    # Format the plot
                    plt.title(f'Time Series of High Concentration Compounds\n{site_name} - {period_info["label"]}',
                            fontsize=16, pad=20)
                    plt.xlabel('Date and Time', fontsize=14)
                    plt.ylabel('Concentration (µg/m³)', fontsize=14)
                    
                    # Format x-axis
                    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
                    plt.xticks(rotation=45, ha='right')
                    
                    # Add grid
                    plt.grid(True, alpha=0.3)
                    
                    # Adjust legend
                    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                             frameon=True, framealpha=0.9, fontsize=10)
                    
                    # Adjust layout
                    plt.tight_layout()
                    
                    # Save the plot
                    plt.savefig(os.path.join(period_dir, f'{site_name}_timeseries_high.png'),
                              bbox_inches='tight', dpi=300)
                else:
                    print(f"No high concentration data found for {site_name}")
                plt.close()
            except Exception as e:
                print(f"Error plotting high concentration time series for {site_name}: {str(e)}")
                plt.close()
    except Exception as e:
        print(f"Error in plot_timeseries for {site_name}: {str(e)}")
        plt.close('all')
    finally:
        plt.close('all')
        gc.collect()

def plot_distributions(data, site_name, period_dir, period_info, low_concentration, high_concentration):
    """Plot distributions for both low and high concentration compounds."""
    # Plot for low concentration compounds
    if low_concentration:
        plt.figure(figsize=(15, 10))
        low_data = data[data['Compound_Name'].isin(low_concentration)].copy()
        low_data['Value'] = low_data['Value'] * 1000
        low_data['Value'] = low_data['Value'].clip(upper=250)
        
        box_data = [low_data[low_data['Compound_Name'] == compound]['Value'].dropna() 
                   for compound in low_concentration]
        
        bp = plt.boxplot(box_data, labels=low_concentration, patch_artist=True)
        
        for i, box in enumerate(bp['boxes']):
            compound = low_concentration[i]
            box.set_facecolor(get_compound_color(compound))
            box.set_alpha(0.8)
        
        plt.title(f'Distribution of Low Concentration Compounds\n{site_name} - {period_info["label"]}')
        plt.xlabel('Compound')
        plt.ylabel('Concentration (ng/m³)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(period_dir, f'{site_name}_distributions_low.png'))
        plt.close()
    
    # Plot for high concentration compounds
    if high_concentration:
        plt.figure(figsize=(15, 10))
        high_data = data[data['Compound_Name'].isin(high_concentration)]
        
        box_data = [high_data[high_data['Compound_Name'] == compound]['Value'].dropna() 
                   for compound in high_concentration]
        
        bp = plt.boxplot(box_data, labels=high_concentration, patch_artist=True)
        
        for i, box in enumerate(bp['boxes']):
            compound = high_concentration[i]
            box.set_facecolor(get_compound_color(compound))
            box.set_alpha(0.8)
        
        plt.title(f'Distribution of High Concentration Compounds\n{site_name} - {period_info["label"]}')
        plt.xlabel('Compound')
        plt.ylabel('Concentration (µg/m³)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(period_dir, f'{site_name}_distributions_high.png'))
        plt.close()

def plot_hourly_patterns(data, site_name, period_dir, period_info, low_concentration, high_concentration):
    """Plot hourly patterns for both low and high concentration compounds."""
    # Plot for low concentration compounds
    if low_concentration:
        plt.figure(figsize=(15, 8))
        low_data = data[data['Compound_Name'].isin(low_concentration)].copy()
        low_data['Value'] = low_data['Value'] * 1000
        low_data['Value'] = low_data['Value'].clip(upper=250)
        
        hourly_avg = low_data.pivot_table(
            values='Value',
            index='Hour',
            columns='Compound_Name',
            aggfunc='mean'
        )
        
        for compound in hourly_avg.columns:
            color = get_compound_color(compound)
            plt.plot(hourly_avg.index, hourly_avg[compound], 
                    label=compound, color=color, alpha=0.7)
        
        plt.title(f'Hourly Patterns - Low Concentration Compounds\n{site_name} - {period_info["label"]}')
        plt.xlabel('Hour of Day')
        plt.ylabel('Average Concentration (ng/m³)')
        plt.xticks(range(0, 24, 2))
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(period_dir, f'{site_name}_hourly_patterns_low.png'))
        plt.close()
    
    # Plot for high concentration compounds
    if high_concentration:
        plt.figure(figsize=(15, 8))
        high_data = data[data['Compound_Name'].isin(high_concentration)]
        
        hourly_avg = high_data.pivot_table(
            values='Value',
            index='Hour',
            columns='Compound_Name',
            aggfunc='mean'
        )
        
        for compound in hourly_avg.columns:
            color = get_compound_color(compound)
            plt.plot(hourly_avg.index, hourly_avg[compound], 
                    label=compound, color=color, alpha=0.7)
        
        plt.title(f'Hourly Patterns - High Concentration Compounds\n{site_name} - {period_info["label"]}')
        plt.xlabel('Hour of Day')
        plt.ylabel('Average Concentration (µg/m³)')
        plt.xticks(range(0, 24, 2))
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(period_dir, f'{site_name}_hourly_patterns_high.png'))
        plt.close()

def plot_correlations(data, site_name, period_dir, period_info, low_concentration, high_concentration):
    """Plot correlations for both low and high concentration compounds."""
    # Plot for low concentration compounds
    if low_concentration:
        plt.figure(figsize=(15, 12))
        low_data = data[data['Compound_Name'].isin(low_concentration)].copy()
        low_data['Value'] = low_data['Value'] * 1000
        
        compound_corr = low_data.pivot_table(
            values='Value',
            index='DateTime',
            columns='Compound_Name',
            aggfunc='mean'
        ).corr()
        
        sns.heatmap(compound_corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True)
        plt.title(f'Compound Correlations - Low Concentration\n{site_name} - {period_info["label"]}')
        plt.tight_layout()
        plt.savefig(os.path.join(period_dir, f'{site_name}_correlations_low.png'))
        plt.close()
    
    # Plot for high concentration compounds
    if high_concentration:
        plt.figure(figsize=(15, 12))
        high_data = data[data['Compound_Name'].isin(high_concentration)]
        
        compound_corr = high_data.pivot_table(
            values='Value',
            index='DateTime',
            columns='Compound_Name',
            aggfunc='mean'
        ).corr()
        
        sns.heatmap(compound_corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True)
        plt.title(f'Compound Correlations - High Concentration\n{site_name} - {period_info["label"]}')
        plt.tight_layout()
        plt.savefig(os.path.join(period_dir, f'{site_name}_correlations_high.png'))
        plt.close()

def main():
    """Main function to analyze specific periods of interest."""
    try:
        print("Starting analysis...")
        
        # Create output directories
        print("Creating output directories...")
        os.makedirs('plots/period_analysis', exist_ok=True)
        
        # Load the data
        print("Loading data...")
        try:
            df = pd.read_csv('data/air_quality_data_with_compounds.csv')
            print(f"Successfully loaded {len(df)} rows of data")
            print(f"Columns: {df.columns.tolist()}")
            
            # Rename columns to use underscores instead of spaces
            df = df.rename(columns={
                'Site name': 'Site_Name',
                'Site ID': 'Site_ID',
                'Parameter Cd': 'Parameter_Code'
            })
            print("Renamed columns for consistency")
            
        except Exception as e:
            print(f"Error loading data file: {str(e)}")
            traceback.print_exc()
            sys.exit(1)
        
        # Process the data
        print("Processing data...")
        try:
            df = process_data(df)
            print("Data processing completed successfully")
            print(f"Processed data shape: {df.shape}")
            print(f"Date range: {df['DateTime'].min()} to {df['DateTime'].max()}")
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            traceback.print_exc()
            sys.exit(1)
        
        # Get unique sites
        sites = df['Site_Name'].unique()
        print(f"Found {len(sites)} sites: {sites}")
        
        # Analyze each period for each site
        for site in sites:
            print(f"\nAnalyzing data for site: {site}")
            try:
                site_data = df[df['Site_Name'] == site].copy()
                print(f"Site data shape: {site_data.shape}")
                
                for period_name, period_info in PERIODS.items():
                    print(f"\nAnalyzing period: {period_info['label']}")
                    try:
                        plot_period_comparison(site_data, site, period_name, period_info)
                        gc.collect()
                    except Exception as e:
                        print(f"Error analyzing period {period_info['label']}: {str(e)}")
                        traceback.print_exc()
                        continue
            except Exception as e:
                print(f"Error analyzing site {site}: {str(e)}")
                traceback.print_exc()
                continue
        
        print("\nAnalysis complete! Check the 'plots/period_analysis' directory for results.")
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("Setting up visualization...")
    setup_visualization()
    main() 