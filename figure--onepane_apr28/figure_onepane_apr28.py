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
    with professionally styled elements, split into two subplots - early afternoon and night.
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

    # Define time ranges for each subplot
    early_end = datetime(2025, 4, 28, 17, 15)
    night_start = datetime(2025, 4, 28, 21, 0)
    night_end = datetime(2025, 4, 29, 2, 0)
    
    # Filter data for each subplot
    data_early = data[(data['Datetime'] <= early_end)].copy()
    data_night = data[(data['Datetime'] >= night_start) & (data['Datetime'] <= night_end)].copy()
    
    print(f"Data early phase: {len(data_early)} rows")
    print(f"Data night phase: {len(data_night)} rows")

    # Create figure with two subplots stacked vertically with equal heights
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=False)

    # Define colors and styling - updated colors per request
    a_pane_color = '#a55194'     # Light purple for A pane bottom
    a_inside_color = '#ff7f7f'   # Light red for A inside bottom
    b_pane_color = '#6a0dad'     # Dark purple for B pane bottom
    b_inside_color = '#b22222'   # Dark red for B inside bottom
    
    # Create the top subplot (early afternoon data)
    # 1. Plot A pane bottom
    ax1.plot(data_early['Datetime'], data_early[temp_columns[0]].astype(float), 
            label='A Pane Bottom', 
            color=a_pane_color, 
            linewidth=2.5,
            zorder=8)
    
    # 2. Plot A inside bottom
    ax1.plot(data_early['Datetime'], data_early[temp_columns[1]].astype(float), 
            label='A Inside Bottom',
            color=a_inside_color, 
            linewidth=2.5,
            zorder=7)
    
    # 3. Plot B pane bottom
    ax1.plot(data_early['Datetime'], data_early[temp_columns[2]].astype(float), 
            label='B Pane Bottom',
            color=b_pane_color, 
            linewidth=2.5,
            zorder=6)
    
    # 4. Plot B inside bottom
    ax1.plot(data_early['Datetime'], data_early[temp_columns[3]].astype(float), 
            label='B Inside Bottom',
            color=b_inside_color, 
            linewidth=2.5,
            zorder=5)

    # Add vertical lines to top subplot
    dotted_times = [
        datetime(2025, 4, 28, 16, 20),
        datetime(2025, 4, 28, 16, 21),
        datetime(2025, 4, 28, 16, 27),
        datetime(2025, 4, 28, 16, 50)
    ]
    
    for t in dotted_times:
        ax1.axvline(t, color='black', linestyle=':', linewidth=1.5, alpha=0.7, zorder=4)
    
    # Add vertical dashed line with horizontal label
    swap_time = datetime(2025, 4, 28, 16, 28)
    ax1.axvline(swap_time, color='black', linestyle='--', linewidth=1.5, alpha=0.7, zorder=4)
    ax1.text(swap_time, 65, 'swap-pos', rotation=0, fontsize=12, 
             verticalalignment='top', horizontalalignment='center',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor=None, boxstyle='round,pad=0.2'))
    
    # Create the bottom subplot (night data)
    # 1. Plot A pane bottom
    ax2.plot(data_night['Datetime'], data_night[temp_columns[0]].astype(float), 
            label='A Pane Bottom', 
            color=a_pane_color, 
            linewidth=2.5,
            zorder=8)
    
    # 2. Plot A inside bottom
    ax2.plot(data_night['Datetime'], data_night[temp_columns[1]].astype(float), 
            label='A Inside Bottom',
            color=a_inside_color, 
            linewidth=2.5,
            zorder=7)
    
    # 3. Plot B pane bottom
    ax2.plot(data_night['Datetime'], data_night[temp_columns[2]].astype(float), 
            label='B Pane Bottom',
            color=b_pane_color, 
            linewidth=2.5,
            zorder=6)
    
    # 4. Plot B inside bottom
    ax2.plot(data_night['Datetime'], data_night[temp_columns[3]].astype(float), 
            label='B Inside Bottom',
            color=b_inside_color, 
            linewidth=2.5,
            zorder=5)

    # Set y-axis limits as specified
    ax1.set_ylim(40, 70)
    ax2.set_ylim(12, 16)
    
    # Set titles for each subplot
    ax1.set_title('One-Pane Experiment, 2025 Apr 28 (Early Afternoon)', fontsize=16, weight='bold', pad=10)
    ax2.set_title('One-Pane Experiment, 2025 Apr 28-29 (Night)', fontsize=16, weight='bold', pad=10)
    
    # Format x-axis with enhanced time display for both subplots
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 30, 45]))
        ax.grid(True, which='major', linestyle='-', alpha=0.3, linewidth=0.8)
        ax.grid(True, which='minor', linestyle=':', alpha=0.2, linewidth=0.5)
    
    # Add axis labels
    ax2.set_xlabel('Time (HH:MM)', fontsize=16, labelpad=10)
    ax1.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)
    ax2.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)
    
    # Add single legend at the top of the figure
    handles, labels = ax1.get_legend_handles_labels()
    legend = fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.98),
                     ncol=4, frameon=True, fancybox=True, shadow=True, 
                     borderpad=0.5, labelspacing=0.4, handlelength=1.2, 
                     handletextpad=1, columnspacing=1)
    legend.get_frame().set_linewidth(0.8)
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, hspace=0.25)
    
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