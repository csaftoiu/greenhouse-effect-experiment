import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import numpy as np
import os 


def create_publication_quality_plot():
    """
    Creates a publication-quality plot of the trial 2 temperature data
    with professionally styled elements and annotations.
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
    csv_fn = os.path.join(data_dir, 'trials2.csv')
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

    # Improved label names and styling
    labels = ['Bottom Pane Topside', 'Bottom Pane Underside', 'Black Bottom', 'Apparatus Underside']
    colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd']  # Professional color palette
    linewidths = [2, 2, 3.5, 2]  # Make black bottom extra bold
    linestyles = ['-', '-', '-', '-']
    
    # Plot data with improved styling - Plot Black Bottom first so it appears first in the legend
    
    # Define the gap times
    gap_start = pd.to_datetime('2024-10-17 13:44:00')
    gap_end = pd.to_datetime('2024-10-17 14:29:00')
    
    # Split data into before and after the gap
    data_before_gap = data[data['Datetime'] < gap_start]
    data_after_gap = data[data['Datetime'] > gap_end]
    
    # First plot Black Bottom (index 2) with gap
    bb_index = 2
    # Plot before gap
    ax.plot(data_before_gap['Datetime'], data_before_gap[temp_columns[bb_index]].astype(float), 
           label=labels[bb_index], 
           color=colors[bb_index], 
           linewidth=linewidths[bb_index],
           linestyle=linestyles[bb_index],
           zorder=10)  # Higher zorder to bring to front
    # Plot after gap - no label to avoid duplicate in legend
    ax.plot(data_after_gap['Datetime'], data_after_gap[temp_columns[bb_index]].astype(float), 
           color=colors[bb_index], 
           linewidth=linewidths[bb_index],
           linestyle=linestyles[bb_index],
           zorder=10)
    
    # Then plot the rest
    for i, column in enumerate(temp_columns):
        if i != bb_index:  # Skip Black Bottom since we already plotted it
            # Plot before gap
            ax.plot(data_before_gap['Datetime'], data_before_gap[column].astype(float), 
                   label=labels[i], 
                   color=colors[i], 
                   linewidth=linewidths[i],
                   linestyle=linestyles[i])
            # Plot after gap - no label to avoid duplicate in legend
            ax.plot(data_after_gap['Datetime'], data_after_gap[column].astype(float), 
                   color=colors[i], 
                   linewidth=linewidths[i],
                   linestyle=linestyles[i])

    # Extract experiment timing information
    experiment_start_time = experiment_start.time()
    print(f"Experiment start time: {experiment_start_time}")

    # Helper functions for time conversion
    def time_str_to_minutes(time_str):
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def minutes_from_experiment_start(time_str):
        time_minutes = time_str_to_minutes(time_str)
        start_minutes = time_str_to_minutes(f"{experiment_start_time.hour}:{experiment_start_time.minute}")
        return time_minutes - start_minutes

    # Define annotations with precise experimental configurations
    print("Setting up annotations...")
    annotations = [
        {
            "config": "CCCC",
            "start_time": "12:21",
            "end_time": "14:30",
            "description": "Clear Bottom Configuration"
        },
        {
            "config": "BBBB",
            "start_time": "14:30",
            "end_time": "15:34",
            "description": "Black Bottom Configuration"
        },
        {
            "config": "CCCC",
            "start_time": "15:34",
            "end_time": "16:25",
            "description": "Clear Bottom Configuration"
        },
        {
            "config": "BBBB",
            "start_time": "16:25",
            "end_time": "17:50",
            "description": "Black Bottom Configuration"
        }
    ]

    # Convert times to minutes from experiment start
    for anno in annotations:
        start_time_str = anno["start_time"]
        end_time_str = anno["end_time"]
        anno["start_min"] = minutes_from_experiment_start(start_time_str)
        anno["end_min"] = minutes_from_experiment_start(end_time_str)
        print(f"{anno['config']} from {start_time_str} to {end_time_str} " +
              f"({anno['end_min'] - anno['start_min']} minutes)")

    # Add annotations as shaded regions with improved styling
    for i, anno in enumerate(annotations):
        # Convert minutes to actual experiment timestamps
        start_time = experiment_start + timedelta(minutes=anno["start_min"])
        end_time = experiment_start + timedelta(minutes=anno["end_min"])
        
        # Check if timestamps are within the data range
        if start_time <= experiment_end and end_time >= experiment_start:
            # If end time exceeds experiment end, cap it
            if end_time > experiment_end:
                end_time = experiment_end
                
            # If start time is before experiment start, cap it
            if start_time < experiment_start:
                start_time = experiment_start
                
            # Improved colors for regions
            if anno["config"] == "CCCC":
                color = '#a6cee3'  # Light blue for clear configuration
                alpha = 0.35
            else:
                color = '#fdbf6f'  # Light orange for black configuration
                alpha = 0.35
                
            ax.axvspan(start_time, end_time, alpha=alpha, color=color, zorder=1)
            
            # Add text annotation in the middle of the span with improved styling
            mid_point = start_time + (end_time - start_time) / 2
            y_max = float(data[temp_columns].max().max())
            y_min = float(data[temp_columns].min().min())
            y_range = y_max - y_min
            
            # Position all labels along the top of the plot
            label_x = mid_point
            y_pos = y_max + 2  # Fixed position 2C above the max temperature value
            
            # Special adjustment for the leftmost CCCC label (first CCCC region)
            if i == 0:  
                # For the first CCCC region, place it at the 13:20 mark (approximate peak)
                # Convert time string to datetime
                peak_time_str = "13:05"  # Time of approximate peak in the first CCCC region
                peak_time = experiment_start.replace(
                    hour=int(peak_time_str.split(':')[0]),
                    minute=int(peak_time_str.split(':')[1])
                )
                label_x = peak_time  # Position label directly above the peak
                y_pos = 49.7

            # Add configuration label - use original CCCC/BBBB format
            ax.text(label_x, y_pos, anno["config"], 
                    horizontalalignment='center', fontsize=12, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5'))
            
            print(f"Added {anno['config']} region from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")

    # Improved plot styling
    ax.set_title('Thermal Response in Experimental Apparatus Configurations', fontsize=18, weight='bold', pad=15)
    ax.set_xlabel('Time (HH:MM)', fontsize=16, labelpad=10)
    ax.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)  # Using proper Unicode degree symbol
    
    # Create legend in top-left with improved styling
    legend = ax.legend(loc='upper left', frameon=True, fancybox=True,
                        shadow=True, borderpad=1, labelspacing=0.8)
    legend.get_frame().set_linewidth(1.5)
    
    # Format x-axis with enhanced time display
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 30, 45]))
    
    # Format y-axis with optimal tick spacing and add 5C of padding
    y_min = data[temp_columns].min().min()
    y_max = data[temp_columns].max().max()
    ax.set_ylim(y_min - 1, y_max + 7)  # Add 5C padding at top for configuration labels
    
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
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure1.png')
    
    fig.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"Done! Figure saved as {save_path}")