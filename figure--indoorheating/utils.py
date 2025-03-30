import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import numpy as np
import os

def set_plot_style():
    """Set publication-quality style parameters for matplotlib"""
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

def format_time(seconds, _):
    """Format seconds to MM:SS format, handling negative values"""
    is_negative = seconds < 0
    seconds_abs = abs(seconds)
    minutes = int(seconds_abs // 60)
    secs = int(seconds_abs % 60)
    
    if is_negative:
        return f"-{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def load_dataset(file_path, name=""):
    """Load and preprocess a dataset from CSV"""
    data = pd.read_csv(file_path, skiprows=3, encoding='latin1')
    print(f"Loaded {len(data)} rows of data from {os.path.basename(file_path)}")
    
    # Convert datetime to proper format
    data['Datetime'] = pd.to_datetime(data.iloc[:, 0])
    print(f"First timestamp{' '+name if name else ''}: {data['Datetime'].iloc[0]}")
    print(f"Last timestamp{' '+name if name else ''}: {data['Datetime'].iloc[-1]}")
    
    return data

def find_target_temp_index(df, temp_col, target_temp):
    """Find the first index where temperature exceeds the target"""
    mask = df[temp_col].astype(float) <= target_temp
    if mask.any():
        return df.index[mask].min()
    else:
        return None

def filter_time_periods(time_periods, start_offset=120, align_to_temp=False, target_temp=None, apparatus_bottom_col=None):
    """Extract and process time periods from datasets"""
    period_data = {}
    reference_points = {}
    
    for period_name, time_range in time_periods.items():
        # Initial filtering with a padding before the start time
        start_time = pd.to_datetime(time_range['start']) - timedelta(seconds=start_offset)
        end_time = pd.to_datetime(time_range['end'])
        
        # Get the appropriate dataset
        source_data = time_range['data']
        
        # Filter data within the time range
        mask = (source_data['Datetime'] >= start_time) & (source_data['Datetime'] <= end_time)
        period_df = source_data[mask].copy()
        
        if not period_df.empty:
            # Calculate seconds from start for this period (with original offset)
            period_df['seconds'] = (period_df['Datetime'] - period_df['Datetime'].iloc[0]).dt.total_seconds()
            
            # Apply the start offset just like before
            period_df['seconds'] = period_df['seconds'] - start_offset
            
            # Store the processed dataframe
            period_data[period_name] = period_df
            print(f"Extracted {len(period_df)} rows for {period_name} period")
            
            # If aligning to temperature, find reference point
            if align_to_temp and target_temp is not None and apparatus_bottom_col is not None:
                target_idx = find_target_temp_index(period_df, apparatus_bottom_col, target_temp)
                
                if target_idx is not None:
                    # Get the timestamp from seconds when the target temp is reached
                    target_seconds = period_df.loc[target_idx, 'seconds']
                    reference_points[period_name] = target_seconds
                    print(f"Found reference point for {period_name} at {target_seconds} seconds from start (temp: {period_df.loc[target_idx, apparatus_bottom_col]}°C)")
                else:
                    print(f"Warning: Could not find temperature {target_temp}°C in {period_name} period!")
                    reference_points[period_name] = None
        else:
            print(f"No data found for {period_name} period!")
    
    # If aligning to temperature, adjust all time series
    if align_to_temp and all(time_point is not None for time_point in reference_points.values()):
        # Find the common alignment point by averaging all reference points
        avg_reference_time = sum(reference_points.values()) / len(reference_points)
        print(f"Average time to reach {target_temp}°C: {avg_reference_time:.2f} seconds")

        # Adjust all time series so that the target temperature point is at t=0
        for period_name, df in period_data.items():
            ref_time = reference_points[period_name]
            time_shift = ref_time - 0  # Shift so that ref_time becomes 0

            # Apply the shift
            df['seconds'] = df['seconds'] - time_shift
            print(f"Shifted {period_name} by {time_shift:.2f} seconds to align to target temperature")

            # Update the DataFrame in the dictionary
            period_data[period_name] = df
    elif align_to_temp:
        print("Warning: Some periods don't reach the target temperature. Skipping additional alignment.")
    
    return period_data

def adjust_color(base_color, darkness, sensor_col, period_name, temp_columns):
    """Adjust color based on sensor and period"""
    # Special handling for apparatus bottom (temp_columns[3])
    if sensor_col == temp_columns[3]:
        if period_name in ['BOROx4', 'CAF2x4', 'BOROx4_65c', 'CAF2x4_65c']:
            return '#000000'  # Black for x4 variants
        else:
            return '#808080'  # Gray for original variants
    
    # For other sensors
    if darkness > 1.0:
        # For darker colors (BOROx4 and CAF2x4)
        rgb = [int(base_color[i:i+2], 16) for i in range(1, 7, 2)]
        # Make color darker by multiplying by 0.7 (70% brightness)
        rgb = [max(0, int(c * 0.7)) for c in rgb]
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    else:
        # For original colors
        return base_color

def create_shorter_version(original_fig, mins, xmin=23, ymax=67, x_label='Time (MM:SS)', figure_title='Cooling rate comparison (first %d minutes)'):
    """Create a version of the figure that shows only -1 to X minutes"""
    # Create a copy of the original figure
    fig = plt.figure(figsize=(16, 12))
    
    # Copy the subplots from the original figure
    for i, ax_orig in enumerate(original_fig.axes):
        # Create a new subplot
        ax_new = fig.add_subplot(2, 2, i+1)
        
        # Copy the lines data from original axis to new axis
        for line in ax_orig.lines:
            # Get the data
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            
            # Filter data to only include -1 to X minutes (-60 to X*60 seconds)
            mask = (x_data >= -60) & (x_data <= mins*60)
            x_filtered = x_data[mask]
            y_filtered = y_data[mask]
            
            # Plot the filtered data on the new axis
            ax_new.plot(
                x_filtered, 
                y_filtered,
                label=line.get_label(),
                color=line.get_color(),
                linestyle=line.get_linestyle(),
                linewidth=line.get_linewidth(),
                zorder=line.get_zorder()
            )
        
        # Copy the title
        ax_new.set_title(ax_orig.get_title(), fontsize=16, weight='bold')
        
        # Copy the grid
        ax_new.grid(True, which='major', linestyle='-', alpha=0.3, linewidth=0.8)
        ax_new.grid(True, which='minor', linestyle=':', alpha=0.2, linewidth=0.5)
        
        # Set y-axis range
        ax_new.set_ylim(xmin, ymax)
        
        # Set x-axis limits to show range from -60 to X*60 seconds (-1 to X minutes)
        ax_new.set_xlim(-60, mins*60)
        
        # Add legend
        ax_new.legend(
            loc='best',
            frameon=True,
            fancybox=True,
            shadow=True,
            borderpad=1,
            labelspacing=0.8
        )
        
        # Add x-label to bottom row subplots
        if i >= 2:
            ax_new.set_xlabel(x_label, fontsize=16, labelpad=10)
        
        # Add y-label to leftmost subplots
        if i % 2 == 0:
            ax_new.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)
        
        # Configure tick formatting
        ax_new.xaxis.set_major_formatter(plt.FuncFormatter(format_time))
        ax_new.xaxis.set_major_locator(mticker.MultipleLocator(120))  # Every 2 minutes
        ax_new.xaxis.set_minor_locator(mticker.MultipleLocator(30))   # Every 30 seconds
        
        # Set y-axis ticks
        ax_new.yaxis.set_major_locator(mticker.MultipleLocator(5))    # Every 5°C
        ax_new.yaxis.set_minor_locator(mticker.MultipleLocator(1))    # Every 1°C
    
    # Add a global title
    fig.suptitle(figure_title % mins, fontsize=20, weight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig