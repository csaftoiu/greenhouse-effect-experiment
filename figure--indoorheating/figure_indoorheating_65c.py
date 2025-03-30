import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import numpy as np
import os

def create_cooling_rate_comparison():
    """
    Creates a publication-quality plot comparing cooling rates for different
    configurations: CAF2x4 and BOROx4, using the Mar29 run65 data.
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
    
    # Load Mar29 run65 data
    csv_fn = os.path.join(data_dir, 'indoor_heating_data_mar29_run65.csv')
    data = pd.read_csv(csv_fn, skiprows=3, encoding='latin1')
    print(f"Loaded {len(data)} rows of data from indoor_heating_data_mar29_run65.csv")
    
    # Load Mar29 run65 v2 data
    csv_fn_v2 = os.path.join(data_dir, 'indoor_heating_data_mar29_run65_v2.csv')
    data_v2 = pd.read_csv(csv_fn_v2, skiprows=3, encoding='latin1')
    print(f"Loaded {len(data_v2)} rows of data from indoor_heating_data_mar29_run65_v2.csv")

    # Convert datetime to proper format
    data['Datetime'] = pd.to_datetime(data.iloc[:, 0])
    print(f"First timestamp: {data['Datetime'].iloc[0]}")
    print(f"Last timestamp: {data['Datetime'].iloc[-1]}")
    
    # Convert datetime for v2 data
    data_v2['Datetime'] = pd.to_datetime(data_v2.iloc[:, 0])
    print(f"First timestamp v2: {data_v2['Datetime'].iloc[0]}")
    print(f"Last timestamp v2: {data_v2['Datetime'].iloc[-1]}")
    
    # Define columns based on header information
    temp_columns = data.columns[2:6]  # Temperature columns
    print(f"Temperature columns: {temp_columns}")

    # Define sensor names from the second row of the file
    sensor_names = ["Air near apparatus", "top pane topside", "black bottom", "apparatus bottom"]
    
    # Define time periods to extract with the specified time ranges
    time_periods = {
        'CAF2x4': {
            'start': '2025-03-29 21:03:41',
            'end': '2025-03-29 21:32:00',
            'data': data_v2
        },
        'BOROx4': {
            'start': '2025-03-29 18:44:03',
            'end': '2025-03-29 19:15:49',
            'data': data
        }
    }
    start_offset = 120

    # Filter data for each time period
    from datetime import timedelta
    period_data = {}
    
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
        else:
            print(f"No data found for {period_name} period!")

    # Define color base for each temperature column
    base_colors = {
        temp_columns[0]: '#00FFFF',  # Air near apparatus - Cyan
        temp_columns[1]: '#00FF00',  # Top pane topside - Green
        temp_columns[2]: '#FF0000',  # Black bottom - Red
        temp_columns[3]: '#808080',  # Apparatus bottom - Gray
    }
    
    # Define line styles for each period
    period_line_styles = {
        'CAF2x4': '--',   # Dashed (like CAF2)
        'BOROx4': '-',    # Solid (like BORO)
    }
    
    # Define darkness levels for each period
    darkness_levels = {
        'CAF2x4': 1.25,   # Darker than CAF2
        'BOROx4': 1.25,   # Darker than BORO
    }
    
    # Adjust color darkness for the data series
    def adjust_color(base_color, darkness, sensor_col, period_name):
        # Special handling for apparatus bottom (temp_columns[3])
        if sensor_col == temp_columns[3]:
            return '#000000'  # Black for x4 variants
        
        # For other sensors
        # For darker colors (BOROx4 and CAF2x4)
        rgb = [int(base_color[i:i+2], 16) for i in range(1, 7, 2)]
        # Make color darker by multiplying by 0.7 (70% brightness)
        rgb = [max(0, int(c * 0.7)) for c in rgb]
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    # Time range to display (from -1 minute to +60 minutes relative to reference point)
    min_seconds = -60  # 1 minute before reference point
    max_seconds = 3600  # 60 minutes after reference point
    
    # Create the figure with 2x2 subplots
    fig, axs = plt.subplots(2, 2, figsize=(16, 12), sharex=True, sharey=True)
    # Flatten the 2x2 array to make iteration easier
    axs = axs.flatten()
    
    # Plot data for each sensor type in a separate subplot
    for j, col in enumerate(temp_columns):
        ax = axs[j]  # Get the appropriate subplot
        
        # Set subplot title to sensor name
        ax.set_title(sensor_names[j], fontsize=16, weight='bold')
        
        # Define the order for plotting periods
        ordered_periods = ['CAF2x4', 'BOROx4']
        
        # Loop through each time period in the specified order
        for i, period_name in enumerate(ordered_periods):
            # Get the dataframe for this period
            if period_name in period_data:
                df = period_data[period_name]
                
                # Filter data to the time range we want to display
                df_filtered = df[(df['seconds'] >= min_seconds) & (df['seconds'] <= max_seconds)]
                
                # Get color for this sensor and adjust based on darkness level
                base_color = base_colors[col]
                color = adjust_color(base_color, darkness_levels[period_name], col, period_name)
                
                # Create label with prefix based on period
                label = f"{period_name}"
                
                # Plot the line
                ax.plot(
                    df_filtered['seconds'], 
                    df_filtered[col].astype(float),
                    label=label,
                    color=color,
                    linestyle=period_line_styles[period_name],  # Line style based on period
                    linewidth=2.5,
                    zorder=10 + i
                )
        
        # Add grid to each subplot
        ax.grid(True, which='major', linestyle='-', alpha=0.3, linewidth=0.8)
        ax.grid(True, which='minor', linestyle=':', alpha=0.2, linewidth=0.5)
        
        # Set y-axis range for each subplot
        ax.set_ylim(23, 67)
        
        # Set x-axis limits to show range from min_seconds to max_seconds
        ax.set_xlim(min_seconds, max_seconds)
        
        # Add legend to each subplot
        ax.legend(
            loc='upper right',
            frameon=True,
            fancybox=True,
            shadow=True,
            borderpad=1,
            labelspacing=0.8
        )
        
        # Only add x-label to bottom row subplots
        if j >= 2:
            ax.set_xlabel('Time from start of trial (MM:SS)', fontsize=16, labelpad=10)
        
        # Only add y-label to leftmost subplots
        if j % 2 == 0:
            ax.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)
        
        # Configure tick formatting
        # Convert x-axis to minutes:seconds format for better readability
        def format_time(seconds, _):
            # Add support for negative time values
            is_negative = seconds < 0
            seconds_abs = abs(seconds)
            minutes = int(seconds_abs // 60)
            secs = int(seconds_abs % 60)
            
            if is_negative:
                return f"-{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"
        
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_time))
        ax.xaxis.set_major_locator(mticker.MultipleLocator(600))  # Every 10 minutes
        ax.xaxis.set_minor_locator(mticker.MultipleLocator(60))   # Every minute
        
        # Set y-axis ticks
        ax.yaxis.set_major_locator(mticker.MultipleLocator(5))    # Every 5°C
        ax.yaxis.set_minor_locator(mticker.MultipleLocator(1))    # Every 1°C
    
    # Add a global title for the entire figure
    fig.suptitle('Cooling rate comparison - 65°C Run', fontsize=20, weight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def create_shorter_version(original_fig, mins, xmin=23):
    """
    Create a version of the figure that shows only -1 to X minutes
    """
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
        ax_new.set_ylim(xmin, 67)
        
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
            ax_new.set_xlabel('Time from start of trial (MM:SS)', fontsize=16, labelpad=10)
        
        # Add y-label to leftmost subplots
        if i % 2 == 0:
            ax_new.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)
        
        # Configure tick formatting
        def format_time(seconds, _):
            # Add support for negative time values
            is_negative = seconds < 0
            seconds_abs = abs(seconds)
            minutes = int(seconds_abs // 60)
            secs = int(seconds_abs % 60)
            
            if is_negative:
                return f"-{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"
        
        ax_new.xaxis.set_major_formatter(plt.FuncFormatter(format_time))
        ax_new.xaxis.set_major_locator(mticker.MultipleLocator(120))  # Every 2 minutes
        ax_new.xaxis.set_minor_locator(mticker.MultipleLocator(30))   # Every 30 seconds
        
        # Set y-axis ticks
        ax_new.yaxis.set_major_locator(mticker.MultipleLocator(5))    # Every 5°C
        ax_new.yaxis.set_minor_locator(mticker.MultipleLocator(1))    # Every 1°C
    
    # Add a global title
    fig.suptitle('Cooling rate comparison - 65°C Run (first %d minutes)' % mins, fontsize=20, weight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

if __name__ == "__main__":
    # Create the publication-quality plot
    fig = create_cooling_rate_comparison()
    
    # Create and save the 10-minute version
    print("Creating 10-minute version of the figure...")
    fig_10m = create_shorter_version(fig, mins=10)

    print("Creating 2-minute version of the figure...")
    fig_2m = create_shorter_version(fig, mins=2, xmin=35)

    # show
    plt.show()

    # Save the figures
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_65c.png')
    fig.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"Done! Figure saved as {save_path}")
    save_path_10m = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_65c_10m.png')
    fig_10m.savefig(save_path_10m, dpi=600, bbox_inches='tight')
    print(f"Done! 10-minute version saved as {save_path_10m}")
    save_path_2m = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_65c_2m.png')
    fig_2m.savefig(save_path_2m, dpi=600, bbox_inches='tight')
    print(f"Done! 2-minute version saved as {save_path_2m}")