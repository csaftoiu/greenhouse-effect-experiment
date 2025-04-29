import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import numpy as np
import os
from scipy.ndimage import uniform_filter1d


def create_publication_quality_plot():
    """
    Creates a publication-quality plot of the one-pane April 28 experiment temperature data
    with professionally styled elements.
    """
    # Set publication-quality style parameters
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': 14,
        'axes.linewidth': 1.5,
        'axes.labelsize': 16,
        'xtick.major.width': 1.5,
        'ytick.major.width': 1.5,
        'xtick.minor.width': 1.0,
        'ytick.minor.width': 1.0,
        'xtick.major.size': 6,
        'ytick.major.size': 6,
        'xtick.minor.size': 3,
        'ytick.minor.size': 3,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 14,
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.edgecolor': 'k',
        'savefig.dpi': 600,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,
        'figure.constrained_layout.use': True
    })

    # Load data
    print("Loading data...")
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    csv_fn = os.path.join(data_dir, 'onepane_apr28.csv')
    data = pd.read_csv(csv_fn, skiprows=3, encoding='latin1')
    print(f"Loaded {len(data)} rows of data")

    # Remove empty or NaN temperature measurements
    data = data.dropna(subset=data.columns[2:6])
    print(f"After dropping NaN: {len(data)} rows")

    # Convert datetime to proper format
    data['Datetime'] = pd.to_datetime(data.iloc[:, 0])
    
    print(f"First timestamp: {data['Datetime'].iloc[0]}")
    print(f"Last timestamp: {data['Datetime'].iloc[-1]}")

    # Calculate experiment duration in minutes
    experiment_start = data['Datetime'].min()
    experiment_end = data['Datetime'].max()
    experiment_duration = (experiment_end - experiment_start).total_seconds() / 60
    print(f"Experiment duration: {experiment_duration:.1f} minutes")

    # Define column names based on actual data
    temp_columns = data.columns[2:6]  # Getting the 4 temperature columns
    print(f"Temperature columns: {temp_columns.tolist()}")

    # Create the high-quality figure with manual positioning
    fig = plt.figure(figsize=(12, 7.5))
    ax = fig.add_axes([0.12, 0.15, 0.82, 0.75])

    # Define colors and styling
    a_pane_color = '#1f77b4'     # Blue for A pane bottom
    a_inside_color = '#2ca02c'    # Green for A inside bottom
    b_pane_color = '#d62728'     # Red for B pane bottom
    b_inside_color = '#9467bd'    # Purple for B inside bottom
    
    # Start plotting, one series at a time with explicit colors and styles
    # 1. Plot A pane bottom
    ax.plot(data['Datetime'], data[temp_columns[0]].astype(float), 
            label='A Pane Bottom', 
            color=a_pane_color, 
            linewidth=2.5,
            zorder=8)
    
    # 2. Plot A inside bottom
    ax.plot(data['Datetime'], data[temp_columns[1]].astype(float), 
            label='A Inside Bottom',
            color=a_inside_color, 
            linewidth=2.5,
            zorder=7)
    
    # 3. Plot B pane bottom
    ax.plot(data['Datetime'], data[temp_columns[2]].astype(float), 
            label='B Pane Bottom',
            color=b_pane_color, 
            linewidth=2.5,
            zorder=6)
    
    # 4. Plot B inside bottom
    ax.plot(data['Datetime'], data[temp_columns[3]].astype(float), 
            label='B Inside Bottom',
            color=b_inside_color, 
            linewidth=2.5,
            zorder=5)

    # Improved plot styling
    ax.set_title('One-Pane Experiment, 2025 Apr 28', fontsize=18, weight='bold', pad=15)
    ax.set_xlabel('Time (HH:MM)', fontsize=16, labelpad=10)
    ax.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)  # Using proper Unicode degree symbol
    
    # Create legend with much smaller size and compact styling
    legend = ax.legend(loc='lower right', frameon=True, fancybox=True,
                       shadow=True, borderpad=0.5, labelspacing=0.4,
                       handlelength=1.2, handletextpad=1,
                       columnspacing=1, ncol=2)
    legend.get_frame().set_linewidth(0.8)
    
    # Format x-axis with enhanced time display
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 30, 45]))
    
    # Format y-axis with optimal tick spacing and add padding
    y_min = data[temp_columns].min().min()
    y_max = data[temp_columns].max().max()
    ax.set_ylim(y_min - 1, y_max + 5)  # Add padding
    
    # Calculate reasonable tick intervals
    temp_range = y_max - y_min
    major_interval = 5 if temp_range > 20 else 2
    minor_interval = major_interval / 5
    
    ax.yaxis.set_major_locator(mticker.MultipleLocator(major_interval))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(minor_interval))
    
    # Add enhanced grid with different levels
    ax.grid(True, which='major', linestyle='-', alpha=0.3, linewidth=0.8)
    ax.grid(True, which='minor', linestyle=':', alpha=0.2, linewidth=0.5)
    
    return fig

if __name__ == "__main__":
    # Create the publication-quality plot
    fig = create_publication_quality_plot()

    plt.show()

    # Save the figure with high resolution for publication
    print("Saving high-resolution figure for publication...")
    
    # Save to the same directory as the script
    import os
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_onepane_apr28.png')
    
    fig.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"Done! Figure saved as {save_path}")