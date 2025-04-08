import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime
import os
from pathlib import Path

# =============================================================================
# Debugging and Error Handling
# =============================================================================
def check_environment():
    """Check if all required directories exist and are accessible."""
    try:
        # Check source directory
        if not os.path.exists('src'):
            print("Warning: 'src' directory not found")
        
        # Check data directory and files
        if not os.path.exists('data'):
            raise ValueError("'data' directory not found")
        data_file = os.path.join('data', 'air_quality_data_with_compounds.csv')
        if not os.path.exists(data_file):
            raise ValueError(f"Data file not found: {data_file}")
        
        # Create plots directory if it doesn't exist
        if not os.path.exists('plots'):
            os.makedirs('plots')
            print("Created 'plots' directory for saving visualizations")
        
        print("Environment check passed successfully")
    except Exception as e:
        print(f"Environment check failed: {str(e)}")
        raise

# =============================================================================
# Visualization Settings
# =============================================================================
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

# =============================================================================
# Data Processing Functions
# =============================================================================
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
        
        # Check for invalid dates
        invalid_dates = df['DateTime'].isna().sum()
        if invalid_dates > 0:
            print(f"Warning: Found {invalid_dates} rows with invalid dates. These will be excluded from analysis.")
            df = df.dropna(subset=['DateTime'])
        
        return df
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        raise

# =============================================================================
# Plotting Functions
# =============================================================================
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

def plot_distributions(data, site_name):
    """Plot box plots showing the distribution of concentrations for each compound."""
    try:
        # Split compounds into two groups based on concentration
        compounds = data['Compound_Name'].unique()
        low_concentration = []
        high_concentration = []
        
        for compound in compounds:
            max_concentration = data[data['Compound_Name'] == compound]['Value'].max()
            if max_concentration < 2:
                low_concentration.append(compound)
            else:
                high_concentration.append(compound)
        
        # Plot for low concentration compounds (in ng/m³)
        if low_concentration:
            plt.figure(figsize=(15, 10))
            low_data = data[data['Compound_Name'].isin(low_concentration)]
            low_data['Value'] = low_data['Value'] * 1000  # Convert to ng/m³
            low_data['Value'] = low_data['Value'].clip(upper=250)  # Limit to 250 ng/m³
            
            box_data = [low_data[low_data['Compound_Name'] == compound]['Value'].dropna() 
                       for compound in low_concentration]
            
            bp = plt.boxplot(box_data, 
                            labels=low_concentration,
                            patch_artist=True,
                            medianprops={'color': 'black', 'linewidth': 2},
                            flierprops={'marker': 'o',
                                      'markerfacecolor': 'grey',
                                      'markeredgecolor': 'grey',
                                      'markersize': 4},
                            whiskerprops={'linewidth': 2},
                            capprops={'linewidth': 2},
                            widths=0.7,
                            boxprops={'linewidth': 2})
            
            for i, box in enumerate(bp['boxes']):
                compound = low_concentration[i]
                box.set_facecolor(get_compound_color(compound))
                box.set_alpha(0.8)
            
            plt.title(f'Distribution of Low Concentration Compounds\nat {site_name}\n(Colored by Refinery Association)\n(Concentrations < 2 µg/m³, shown in ng/m³, limited to 250 ng/m³)', 
                     fontsize=16, pad=20)
            plt.xlabel('Compound', fontsize=14)
            plt.ylabel('Concentration (ng/m³, limited to 250)', fontsize=14)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.yticks(fontsize=10)
            
            legend_elements = [plt.Rectangle((0,0), 1, 1, 
                                          facecolor=color, 
                                          alpha=0.8,
                                          linewidth=2,
                                          label=category)
                             for category, color in CATEGORY_COLORS.items()]
            plt.legend(handles=legend_elements, 
                      loc='upper right', 
                      title='Compound Categories',
                      title_fontsize=12,
                      fontsize=10)
            
            plt.tight_layout()
            plt.savefig(os.path.join('plots', f'{site_name}_distributions_low.png'), 
                        bbox_inches='tight', 
                        dpi=300)
            plt.close()
        
        # Plot for high concentration compounds (in µg/m³)
        if high_concentration:
            plt.figure(figsize=(15, 10))
            high_data = data[data['Compound_Name'].isin(high_concentration)]
            
            box_data = [high_data[high_data['Compound_Name'] == compound]['Value'].dropna() 
                       for compound in high_concentration]
            
            bp = plt.boxplot(box_data, 
                            labels=high_concentration,
                            patch_artist=True,
                            medianprops={'color': 'black', 'linewidth': 2},
                            flierprops={'marker': 'o',
                                      'markerfacecolor': 'grey',
                                      'markeredgecolor': 'grey',
                                      'markersize': 4},
                            whiskerprops={'linewidth': 2},
                            capprops={'linewidth': 2},
                            widths=0.7,
                            boxprops={'linewidth': 2})
            
            for i, box in enumerate(bp['boxes']):
                compound = high_concentration[i]
                box.set_facecolor(get_compound_color(compound))
                box.set_alpha(0.8)
            
            plt.title(f'Distribution of High Concentration Compounds\nat {site_name}\n(Colored by Refinery Association)\n(Concentrations ≥ 2 µg/m³)', 
                     fontsize=16, pad=20)
            plt.xlabel('Compound', fontsize=14)
            plt.ylabel('Concentration (µg/m³)', fontsize=14)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.yticks(fontsize=10)
            
            legend_elements = [plt.Rectangle((0,0), 1, 1, 
                                          facecolor=color, 
                                          alpha=0.8,
                                          linewidth=2,
                                          label=category)
                             for category, color in CATEGORY_COLORS.items()]
            plt.legend(handles=legend_elements, 
                      loc='upper right', 
                      title='Compound Categories',
                      title_fontsize=12,
                      fontsize=10)
            
            plt.tight_layout()
            plt.savefig(os.path.join('plots', f'{site_name}_distributions_high.png'), 
                        bbox_inches='tight', 
                        dpi=300)
            plt.close()
            
    except Exception as e:
        print(f"Error plotting distributions for {site_name}: {str(e)}")

def plot_hourly_patterns(data, site_name):
    """Plot line charts showing how concentrations vary throughout the day."""
    try:
        # Split compounds into two groups based on concentration
        compounds = data['Compound_Name'].unique()
        low_concentration = []
        high_concentration = []
        
        for compound in compounds:
            max_concentration = data[data['Compound_Name'] == compound]['Value'].max()
            if max_concentration < 2:
                low_concentration.append(compound)
            else:
                high_concentration.append(compound)
        
        # Plot for low concentration compounds (in ng/m³)
        if low_concentration:
            plt.figure(figsize=(15, 8))
            low_data = data[data['Compound_Name'].isin(low_concentration)]
            low_data['Value'] = low_data['Value'] * 1000  # Convert to ng/m³
            low_data['Value'] = low_data['Value'].clip(upper=250)  # Limit to 250 ng/m³
            
            hourly_avg = low_data.pivot_table(
                values='Value',
                index='Hour',
                columns='Compound_Name',
                aggfunc='mean'
            )
            
            for compound in hourly_avg.columns:
                color = get_compound_color(compound)
                linestyle = '--' if compound not in REFINERY_COMPOUNDS else '-'
                alpha = 1.0 if compound in REFINERY_COMPOUNDS else 0.3
                plt.plot(hourly_avg.index, hourly_avg[compound], 
                        label=compound, linewidth=2, color=color,
                        linestyle=linestyle, alpha=alpha)
            
            plt.title(f'Hourly Patterns of Low Concentration Compounds\nat {site_name}\n(Refinery Compounds Highlighted)\n(Concentrations < 2 µg/m³, shown in ng/m³, limited to 250 ng/m³)', 
                     fontsize=16, pad=20)
            plt.xlabel('Hour of Day', fontsize=14)
            plt.ylabel('Average Concentration (ng/m³, limited to 250)', fontsize=14)
            plt.xticks(range(0, 24, 2), fontsize=10)
            plt.yticks(fontsize=10)
            
            legend_elements = [plt.Line2D([0], [0], color=color, label=category, linewidth=2)
                             for category, color in CATEGORY_COLORS.items()]
            plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), 
                      loc='upper left', title='Compound Categories')
            
            plt.tight_layout()
            plt.savefig(os.path.join('plots', f'{site_name}_hourly_patterns_low.png'), 
                        bbox_inches='tight')
            plt.close()
        
        # Plot for high concentration compounds (in µg/m³)
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
                linestyle = '--' if compound not in REFINERY_COMPOUNDS else '-'
                alpha = 1.0 if compound in REFINERY_COMPOUNDS else 0.3
                plt.plot(hourly_avg.index, hourly_avg[compound], 
                        label=compound, linewidth=2, color=color,
                        linestyle=linestyle, alpha=alpha)
            
            plt.title(f'Hourly Patterns of High Concentration Compounds\nat {site_name}\n(Refinery Compounds Highlighted)\n(Concentrations ≥ 2 µg/m³)', 
                     fontsize=16, pad=20)
            plt.xlabel('Hour of Day', fontsize=14)
            plt.ylabel('Average Concentration (µg/m³)', fontsize=14)
            plt.xticks(range(0, 24, 2), fontsize=10)
            plt.yticks(fontsize=10)
            
            legend_elements = [plt.Line2D([0], [0], color=color, label=category, linewidth=2)
                             for category, color in CATEGORY_COLORS.items()]
            plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), 
                      loc='upper left', title='Compound Categories')
            
            plt.tight_layout()
            plt.savefig(os.path.join('plots', f'{site_name}_hourly_patterns_high.png'), 
                        bbox_inches='tight')
            plt.close()
            
    except Exception as e:
        print(f"Error plotting hourly patterns for {site_name}: {str(e)}")

def plot_weekly_patterns(data, site_name):
    """Plot line charts showing concentration variations by day of the week."""
    try:
        # Split compounds into two groups based on concentration
        compounds = data['Compound_Name'].unique()
        low_concentration = []
        high_concentration = []
        
        for compound in compounds:
            max_concentration = data[data['Compound_Name'] == compound]['Value'].max()
            if max_concentration < 2:
                low_concentration.append(compound)
            else:
                high_concentration.append(compound)
        
        # Plot for low concentration compounds (in ng/m³)
        if low_concentration:
            plt.figure(figsize=(15, 8))
            low_data = data[data['Compound_Name'].isin(low_concentration)]
            low_data['Value'] = low_data['Value'] * 1000  # Convert to ng/m³
            low_data['Value'] = low_data['Value'].clip(upper=250)  # Limit to 250 ng/m³
            
            daily_avg = low_data.pivot_table(
                values='Value',
                index='DayOfWeek',
                columns='Compound_Name',
                aggfunc='mean'
            )
            
            for compound in daily_avg.columns:
                plt.plot(daily_avg.index, daily_avg[compound], 
                        label=compound, linewidth=2)
            
            plt.title(f'Weekly Patterns of Low Concentration Compounds\nat {site_name}\n(Concentrations < 2 µg/m³, shown in ng/m³, limited to 250 ng/m³)', 
                     fontsize=16, pad=20)
            plt.xlabel('Day of Week', fontsize=14)
            plt.ylabel('Average Concentration (ng/m³, limited to 250)', fontsize=14)
            plt.xticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 
                      fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(os.path.join('plots', f'{site_name}_weekly_patterns_low.png'), 
                        bbox_inches='tight')
            plt.close()
        
        # Plot for high concentration compounds (in µg/m³)
        if high_concentration:
            plt.figure(figsize=(15, 8))
            high_data = data[data['Compound_Name'].isin(high_concentration)]
            
            daily_avg = high_data.pivot_table(
                values='Value',
                index='DayOfWeek',
                columns='Compound_Name',
                aggfunc='mean'
            )
            
            for compound in daily_avg.columns:
                plt.plot(daily_avg.index, daily_avg[compound], 
                        label=compound, linewidth=2)
            
            plt.title(f'Weekly Patterns of High Concentration Compounds\nat {site_name}\n(Concentrations ≥ 2 µg/m³)', 
                     fontsize=16, pad=20)
            plt.xlabel('Day of Week', fontsize=14)
            plt.ylabel('Average Concentration (µg/m³)', fontsize=14)
            plt.xticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 
                      fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(os.path.join('plots', f'{site_name}_weekly_patterns_high.png'), 
                        bbox_inches='tight')
            plt.close()
            
    except Exception as e:
        print(f"Error plotting weekly patterns for {site_name}: {str(e)}")

def plot_monthly_trends(data, site_name):
    """Plot line charts showing seasonal variations in concentrations."""
    try:
        # Split compounds into two groups based on concentration
        compounds = data['Compound_Name'].unique()
        low_concentration = []
        high_concentration = []
        
        for compound in compounds:
            max_concentration = data[data['Compound_Name'] == compound]['Value'].max()
            if max_concentration < 2:
                low_concentration.append(compound)
            else:
                high_concentration.append(compound)
        
        # Plot for low concentration compounds (in ng/m³)
        if low_concentration:
            plt.figure(figsize=(15, 8))
            low_data = data[data['Compound_Name'].isin(low_concentration)]
            low_data['Value'] = low_data['Value'] * 1000  # Convert to ng/m³
            low_data['Value'] = low_data['Value'].clip(upper=250)  # Limit to 250 ng/m³
            
            monthly_avg = low_data.pivot_table(
                values='Value',
                index='Month',
                columns='Compound_Name',
                aggfunc='mean'
            )
            
            for compound in monthly_avg.columns:
                plt.plot(monthly_avg.index, monthly_avg[compound], 
                        label=compound, linewidth=2)
            
            plt.title(f'Monthly Trends of Low Concentration Compounds\nat {site_name}\n(Concentrations < 2 µg/m³, shown in ng/m³, limited to 250 ng/m³)', 
                     fontsize=16, pad=20)
            plt.xlabel('Month', fontsize=14)
            plt.ylabel('Average Concentration (ng/m³, limited to 250)', fontsize=14)
            plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
                      fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(os.path.join('plots', f'{site_name}_monthly_trends_low.png'), 
                        bbox_inches='tight')
            plt.close()
        
        # Plot for high concentration compounds (in µg/m³)
        if high_concentration:
            plt.figure(figsize=(15, 8))
            high_data = data[data['Compound_Name'].isin(high_concentration)]
            
            monthly_avg = high_data.pivot_table(
                values='Value',
                index='Month',
                columns='Compound_Name',
                aggfunc='mean'
            )
            
            for compound in monthly_avg.columns:
                plt.plot(monthly_avg.index, monthly_avg[compound], 
                        label=compound, linewidth=2)
            
            plt.title(f'Monthly Trends of High Concentration Compounds\nat {site_name}\n(Concentrations ≥ 2 µg/m³)', 
                     fontsize=16, pad=20)
            plt.xlabel('Month', fontsize=14)
            plt.ylabel('Average Concentration (µg/m³)', fontsize=14)
            plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
                      fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(os.path.join('plots', f'{site_name}_monthly_trends_high.png'), 
                        bbox_inches='tight')
            plt.close()
            
    except Exception as e:
        print(f"Error plotting monthly trends for {site_name}: {str(e)}")

def plot_correlation_heatmap(data, site_name):
    """Plot a heatmap showing relationships between different compounds."""
    try:
        plt.figure(figsize=(15, 12))
        
        # Calculate correlations between compounds
        compound_corr = data.pivot_table(
            values='Value',
            index='DateTime',
            columns='Compound_Name',
            aggfunc='mean'
        ).corr()
        
        # Create heatmap with upper triangle masked
        mask = np.triu(np.ones_like(compound_corr, dtype=bool))
        plt.imshow(compound_corr, cmap='coolwarm', vmin=-1, vmax=1)
        plt.colorbar(label='Correlation')
        
        # Add correlation values
        for i in range(len(compound_corr)):
            for j in range(len(compound_corr)):
                if not mask[i, j]:
                    plt.text(j, i, f'{compound_corr.iloc[i, j]:.2f}', 
                            ha='center', va='center', color='black')
        
        plt.title(f'Correlation Between Compounds\nat {site_name}', 
                 fontsize=16, pad=20)
        plt.xticks(range(len(compound_corr)), compound_corr.columns, 
                  rotation=45, ha='right')
        plt.yticks(range(len(compound_corr)), compound_corr.columns)
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'{site_name}_correlation.png'), bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error plotting correlation heatmap for {site_name}: {str(e)}")

def plot_compound_correlations(data, site_name):
    """Create correlation matrix heatmap for all compounds."""
    try:
        # Select only numeric compound columns
        compound_cols = [col for col in data.columns 
                        if col not in ['Date', 'Time', 'Site', 'Wind Speed', 'Wind Direction']
                        and pd.api.types.is_numeric_dtype(data[col])]
        
        if not compound_cols:
            print(f"No numeric compound columns found for {site_name}, skipping correlations plot")
            return
            
        corr_matrix = data[compound_cols].corr()
        
        plt.figure(figsize=(15, 12))
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            cbar_kws={'shrink': 0.8}
        )
        plt.title(f'Compound Correlations - {site_name}', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'{site_name}_compound_correlations.png'), bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"Error creating compound correlations plot for {site_name}: {str(e)}")

def plot_concentration_heatmap(data, site_name):
    """Create heatmap of compound concentrations over time."""
    try:
        # Select only numeric compound columns
        compound_cols = [col for col in data.columns 
                        if col not in ['Date', 'Time', 'Site', 'Wind Speed', 'Wind Direction']
                        and pd.api.types.is_numeric_dtype(data[col])]
        
        if not compound_cols:
            print(f"No numeric compound columns found for {site_name}, skipping concentration heatmap")
            return
            
        # Convert Date to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(data['Date']):
            data['Date'] = pd.to_datetime(data['Date'])
            
        # Resample to daily averages
        daily_data = data.set_index('Date')[compound_cols].resample('D').mean()
        
        plt.figure(figsize=(15, 8))
        sns.heatmap(
            daily_data.T,
            cmap='YlOrRd',
            cbar_kws={'label': 'Concentration (µg/m³)'}
        )
        plt.title(f'Daily Compound Concentrations - {site_name}', pad=20)
        plt.xlabel('Date')
        plt.ylabel('Compound')
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'{site_name}_concentration_heatmap.png'), bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"Error creating concentration heatmap for {site_name}: {str(e)}")

def plot_original_distributions(data, site_name):
    """Plot original box plots without refinery classification."""
    try:
        plt.figure(figsize=(15, 10))
        
        compounds = data['Compound_Name'].unique()
        box_data = [data[data['Compound_Name'] == compound]['Value'].dropna() 
                   for compound in compounds]
        
        # Create box plot with uniform styling
        bp = plt.boxplot(box_data, 
                        labels=compounds,
                        patch_artist=True,
                        medianprops={'color': 'black', 'linewidth': 2},
                        flierprops={'marker': 'o',
                                  'markerfacecolor': 'grey',
                                  'markeredgecolor': 'grey',
                                  'markersize': 4},
                        whiskerprops={'linewidth': 2},
                        capprops={'linewidth': 2},
                        widths=0.7,
                        boxprops={'linewidth': 2})
        
        # Use uniform color for all boxes
        for box in bp['boxes']:
            box.set_facecolor('#4ECDC4')  # Teal color
            box.set_alpha(0.7)
        
        plt.title(f'Distribution of Air Quality Compounds\nat {site_name}\n(Original Version)\n(Concentrations limited to 15 µg/m³)', 
                 fontsize=16, pad=20)
        plt.xlabel('Compound', fontsize=14)
        plt.ylabel('Concentration (limited to 15)', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'{site_name}_distributions_original.png'), 
                    bbox_inches='tight', 
                    dpi=300)
        plt.close()
    except Exception as e:
        print(f"Error plotting original distributions for {site_name}: {str(e)}")

def plot_original_hourly_patterns(data, site_name):
    """Plot original hourly patterns without refinery classification."""
    try:
        plt.figure(figsize=(15, 8))
        
        hourly_avg = data.pivot_table(
            values='Value',
            index='Hour',
            columns='Compound_Name',
            aggfunc='mean'
        )
        
        # Plot hourly patterns with uniform styling
        for compound in hourly_avg.columns:
            plt.plot(hourly_avg.index, hourly_avg[compound], 
                    label=compound, linewidth=2, color='#4ECDC4', alpha=0.7)
        
        plt.title(f'Hourly Patterns of Air Quality Compounds\nat {site_name}\n(Original Version)\n(Concentrations limited to 15 µg/m³)', 
                 fontsize=16, pad=20)
        plt.xlabel('Hour of Day', fontsize=14)
        plt.ylabel('Average Concentration (limited to 15)', fontsize=14)
        plt.xticks(range(0, 24, 2), fontsize=10)
        plt.yticks(fontsize=10)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(os.path.join('plots', f'{site_name}_hourly_patterns_original.png'), 
                    bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error plotting original hourly patterns for {site_name}: {str(e)}")

# =============================================================================
# Main Analysis
# =============================================================================
def main():
    """Main function to run the analysis."""
    try:
        print("\n=== Starting Air Quality Analysis ===\n")
        
        # Check environment and setup
        print("Checking environment...")
        check_environment()
        
        print("\nConfiguring visualization settings...")
        setup_visualization()
        
        # Read and validate data
        print("\nLoading data...")
        data_file = os.path.join('data', 'air_quality_data_with_compounds.csv')
        print(f"Reading from: {os.path.abspath(data_file)}")
        df = pd.read_csv(data_file)
        print(f"Data loaded successfully: {len(df)} rows")
        
        # Check for required columns
        required_columns = ['Site ID', 'Site name', 'Parameter Cd', 'Compound_Name', 
                           'Date', 'Time', 'Value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        print("All required columns found")
        
        # Display available columns
        print("\nAvailable columns:")
        for col in df.columns:
            print(f"- {col}")
        
        # Process data
        print("\nProcessing data...")
        df = process_data(df)
        print("Data processing complete")
        
        # Get unique sites
        sites = df['Site name'].unique()
        print(f"\nFound {len(sites)} sites: {', '.join(sites)}")
        
        # Generate plots for each site
        print("\nGenerating plots...")
        for site in sites:
            site_data = df[df['Site name'] == site]
            print(f"\nProcessing {site}...")
            print(f"Number of records: {len(site_data)}")
            
            # Original plots (without refinery classification)
            print("- Generating original distribution plot...")
            plot_original_distributions(site_data, site)
            
            print("- Generating original hourly patterns plot...")
            plot_original_hourly_patterns(site_data, site)
            
            # New plots (with refinery classification)
            print("- Generating refinery-classified distribution plot...")
            plot_distributions(site_data, site)
            
            print("- Generating refinery-classified hourly patterns plot...")
            plot_hourly_patterns(site_data, site)
            
            # Other plots
            print("- Generating weekly patterns plot...")
            plot_weekly_patterns(site_data, site)
            
            print("- Generating monthly trends plot...")
            plot_monthly_trends(site_data, site)
            
            print("- Generating correlation heatmap...")
            plot_correlation_heatmap(site_data, site)
            
            print("- Generating compound correlations plot...")
            plot_compound_correlations(site_data, site)
            
            print("- Generating concentration heatmap...")
            plot_concentration_heatmap(site_data, site)
            
            print(f"Completed processing {site}")
        
        print("\n=== Analysis complete! ===")
        print("Check the 'plots' directory for visualizations.")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please check the error message above and try again.")
        raise  # Re-raise the exception for full traceback

if __name__ == "__main__":
    main() 