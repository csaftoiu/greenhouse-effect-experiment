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
    Creates a publication-quality plot of the resync experiment temperature data
    with professionally styled elements, region annotations and adjustment markers.
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
    csv_fn = os.path.join(data_dir, 'resync.csv')
    data = pd.read_csv(csv_fn, skiprows=3, encoding='latin1')
    print(f"Loaded {len(data)} rows of data")

    # Remove empty or NaN temperature measurements
    data = data.dropna(subset=data.columns[2:6])
    print(f"After dropping NaN: {len(data)} rows")

    # Convert datetime to proper format
    data['Datetime'] = pd.to_datetime(data.iloc[:, 0])
    
    # Apply time offset correction to make 17:30 map to 18:23
    # The difference is 0:53
    time_offset = timedelta(hours=0, minutes=53)
    data['Datetime'] = data['Datetime'] + time_offset
    
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
    labels = ['Outside Air', 'Outside Air (15-min avg)', 'Bottom of Pane', 'Black Bottom', 'Apparatus Bottom']
    colors = ['#1f77b4', '#0a4c8c', '#2ca02c', '#d62728', '#9467bd']  # Professional color palette with darker blue for avg
    linewidths = [2, 2.5, 2, 3.5, 2]  # Make black bottom extra bold and avg slightly thicker
    linestyles = ['-', '-', '-', '-', '-']
    
    # Plot data with improved styling - Plot Black Bottom first so it appears first in the legend
    bb_index = 3  # Updated index for Black Bottom (was 2)
    outside_air_index = 0
    
    # Create 15-minute weighted moving average of outside air temperature
    # First convert to seconds between measurements
    outside_air_temps = data[temp_columns[outside_air_index]].astype(float).values
    
    # Calculate sampling frequency (samples per second) based on first 100 data points
    time_diffs = []
    for i in range(1, min(100, len(data))):
        time_diff = (data['Datetime'].iloc[i] - data['Datetime'].iloc[i-1]).total_seconds()
        time_diffs.append(time_diff)
    avg_time_diff = np.mean(time_diffs)
    
    # Calculate window size for 15 minutes
    window_size = int(15 * 60 / avg_time_diff)
    print(f"Using window size of {window_size} for 15-minute moving average (avg sampling: {avg_time_diff:.2f}s)")
    
    # Create weighted average using uniform filter (simple moving average for now)
    outside_air_avg = uniform_filter1d(outside_air_temps, size=window_size, mode='nearest')
    
    # Plot Black Bottom first for consistent legend ordering
    ax.plot(data['Datetime'], data[temp_columns[bb_index]].astype(float), 
            label=labels[bb_index], 
            color=colors[bb_index], 
            linewidth=linewidths[bb_index],
            linestyle=linestyles[bb_index],
            zorder=10)  # Higher zorder to bring to front
    
    # Plot Outside Air
    ax.plot(data['Datetime'], outside_air_temps, 
           label=labels[outside_air_index], 
           color=colors[outside_air_index], 
           linewidth=linewidths[outside_air_index],
           linestyle=linestyles[outside_air_index])
    
    # Plot Outside Air 15-min average
    ax.plot(data['Datetime'], outside_air_avg, 
           label=labels[1],  # Outside Air (15-min avg) 
           color=colors[1], 
           linewidth=linewidths[1],
           linestyle=linestyles[1],
           zorder=8)  # Higher zorder to make it more visible
    
    # Then plot the rest
    for i, column in enumerate(temp_columns):
        if i != bb_index and i != outside_air_index:  # Skip Black Bottom and Outside Air since we already plotted them
            ax.plot(data['Datetime'], data[column].astype(float), 
                   label=labels[i+1],  # +1 to account for the avg line 
                   color=colors[i+1], 
                   linewidth=linewidths[i+1],
                   linestyle=linestyles[i+1])

    # Load adjustment data
    adjusts_fn = os.path.join(data_dir, 'adjusts.csv')
    adjusts = pd.read_csv(adjusts_fn)
    print(f"Loaded {len(adjusts)} adjustment points")
    
    # Extract experiment date from data
    experiment_date = experiment_start.date()
    
    # Process adjusts data to create glass type regions and adjustment markers
    glass_regions = []
    adjustments = []
    
    current_glass = None
    region_start = None
    
    for _, row in adjusts.iterrows():
        time_str = row['time']
        adjustment_type = row['adjustment_type']
        
        # Convert time string to datetime
        if ':' in time_str:
            hour, minute = map(int, time_str.split(':'))
        else:
            # Handle format like "1:06" which might be parsed as "1"
            parts = time_str.split(':')
            if len(parts) == 1:
                hour = int(parts[0])
                minute = 0
            else:
                hour, minute = map(int, parts)
                
        # Handle PM times (assuming experiment doesn't run past midnight)
        if hour < 9:  # If hour is less than start hour, assume PM
            hour += 12
            
        timestamp = datetime.combine(experiment_date, 
                                    datetime.min.time().replace(hour=hour, minute=minute))
        
        if adjustment_type in ['boro', 'caf2']:
            # If this is a glass type change, add to regions
            if current_glass is not None:
                # Close the previous region
                glass_regions.append({
                    'type': current_glass,
                    'start': region_start,
                    'end': timestamp
                })
            
            # Start a new region
            current_glass = adjustment_type
            region_start = timestamp
        
        if adjustment_type == 'adjust':
            # Add adjustment marker
            adjustments.append(timestamp)
    
    # Add the final region if there is one
    if current_glass is not None and region_start is not None:
        glass_regions.append({
            'type': current_glass,
            'start': region_start,
            'end': experiment_end
        })
    
    # Add glass type regions as shaded areas
    for region in glass_regions:
        if region['type'] == 'boro':
            color = '#a6cee3'  # Light blue for boro configuration (same as CCCC)
            alpha = 0.35
        else:  # caf2
            color = '#fdbf6f'  # Light orange for caf2 configuration (same as BBBB)
            alpha = 0.35
            
        ax.axvspan(region['start'], region['end'], alpha=alpha, color=color, zorder=1)
        
        # Add text annotation in the middle of the span
        mid_point = region['start'] + (region['end'] - region['start']) / 2
        y_max = float(data[temp_columns].max().max())
        
        # Position label along the top of the plot
        ax.text(mid_point, y_max + 2, region['type'].upper(), 
                horizontalalignment='center', fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5'))
        
        print(f"Added {region['type']} region from {region['start'].strftime('%H:%M')} to {region['end'].strftime('%H:%M')}")
    
    # Add adjustment markers as vertical dotted lines
    for adj_time in adjustments:
        ax.axvline(adj_time, color='black', linestyle=':', linewidth=1, alpha=0.7, zorder=5)
        print(f"Added adjustment marker at {adj_time.strftime('%H:%M')}")

    # Improved plot styling
    ax.set_title('Thermal Response, 2025 Apr 26, 1 pane', fontsize=18, weight='bold', pad=15)
    ax.set_xlabel('Time (HH:MM)', fontsize=16, labelpad=10)
    ax.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)  # Using proper Unicode degree symbol
    
    # Create legend with much smaller size and compact styling
    legend = ax.legend(loc='lower right', frameon=True, fancybox=True,
                       shadow=True, borderpad=0.3, labelspacing=0.2,
                       handlelength=1.2, handletextpad=0.4,
                       columnspacing=1, ncol=2)
    legend.get_frame().set_linewidth(0.8)
    
    # Format x-axis with enhanced time display
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 30, 45]))
    
    # Format y-axis with optimal tick spacing and add padding
    y_min = data[temp_columns].min().min()
    y_max = data[temp_columns].max().max()
    ax.set_ylim(y_min - 1, y_max + 7)  # Add padding at top for configuration labels
    
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
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_resyncexp.png')
    
    fig.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"Done! Figure saved as {save_path}")