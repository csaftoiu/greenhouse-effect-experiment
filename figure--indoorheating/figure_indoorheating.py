import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import numpy as np
import os

TARGET_TEMP = 44.0

def create_cooling_rate_comparison():
    """
    Creates a publication-quality plot comparing cooling rates for different
    configurations: NOPANE, CAF2, and BORO. Split into 4 subplots, one for each sensor.
    """
    # Set publication-quality style parameters (similar to figure-sep13exp.py)
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
    csv_fn = os.path.join(data_dir, 'indoor_heating_data.csv')
    data = pd.read_csv(csv_fn, skiprows=3, encoding='latin1')
    print(f"Loaded {len(data)} rows of data")

    # Convert datetime to proper format
    data['Datetime'] = pd.to_datetime(data.iloc[:, 0])
    print(f"First timestamp: {data['Datetime'].iloc[0]}")
    print(f"Last timestamp: {data['Datetime'].iloc[-1]}")
    
    # Define columns based on header information
    temp_columns = data.columns[2:6]  # Temperature columns
    print(f"Temperature columns: {temp_columns}")

    # Define sensor names from the second row of the file
    sensor_names = ["Air near apparatus", "top pane topside", "black bottom", "apparatus bottom"]

    # Define time periods to extract (as specified in the requirements)
    time_periods = {
        'NOPANE': {
            'start': '2025-03-28 17:02:57',
            'end': '2025-03-28 17:34:16',
        },
        'CAF2': {
            'start': '2025-03-28 18:27:27',
            'end': '2025-03-28 19:29:00',
        },
        'BORO': {
            'start': '2025-03-28 20:05:20',
            'end': '2025-03-28 20:59:34',
        }
    }
    start_offset = 120

    # Filter data for each time period
    from datetime import timedelta
    period_data = {}
    for period_name, time_range in time_periods.items():
        start_time = pd.to_datetime(time_range['start']) - timedelta(seconds=start_offset)
        end_time = pd.to_datetime(time_range['end'])
        
        # Filter data within the time range
        mask = (data['Datetime'] >= start_time) & (data['Datetime'] <= end_time)
        period_df = data[mask].copy()
        
        if not period_df.empty:
            # Calculate seconds from start for this period
            period_df['seconds'] = (period_df['Datetime'] - period_df['Datetime'].iloc[0]).dt.total_seconds()
            period_data[period_name] = period_df
            print(f"Extracted {len(period_df)} rows for {period_name} period")
        else:
            print(f"No data found for {period_name} period!")
    
    # Align all periods to start offset point
    # Find reference points and adjust time values
    for period_name, df in period_data.items():
        df['seconds'] = df['seconds'] - start_offset

        # Update the DataFrame in the dictionary
        period_data[period_name] = df

    # Define color base for each temperature column
    base_colors = {
        temp_columns[0]: '#00FFFF',  # Air near apparatus - Cyan
        temp_columns[1]: '#00FF00',  # Top pane topside - Green
        temp_columns[2]: '#FF0000',  # Black bottom - Red
        temp_columns[3]: '#000000',  # Apparatus bottom - Black
    }
    
    # Define line styles for each period
    period_line_styles = {
        'NOPANE': ':',    # Dotted
        'CAF2': '--',     # Dashed
        'BORO': '-',      # Solid
    }
    
    # Define darkness levels for each period
    darkness_levels = {
        'NOPANE': 0.5,   # Lighter
        'CAF2': 0.75,    # Medium
        'BORO': 1.0,     # Darker
    }
    
    # No longer adjusting color shades - using the same shade for all periods
    def adjust_color(base_color, darkness):
        # Return the original color regardless of darkness level
        return base_color
    
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
        
        # Loop through each time period and plot on this subplot
        for i, (period_name, df) in enumerate(period_data.items()):
            # Filter data to the time range we want to display
            df_filtered = df[(df['seconds'] >= min_seconds) & (df['seconds'] <= max_seconds)]
            
            # Get color for this sensor
            color = base_colors[col]
            
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
        ax.set_ylim(23, 46)
        
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
            ax.set_xlabel('Time relative to room temp sensor starting to drop (MM:SS)', fontsize=16, labelpad=10)
        
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
    fig.suptitle('Cooling rate comparison', fontsize=20, weight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def create_shorter_version(original_fig, mins, xmin=23):
    """
    Create a version of the figure that shows only -1 to 10 minutes
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
            
            # Filter data to only include -1 to 10 minutes (-60 to 600 seconds)
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
        ax_new.set_ylim(xmin, 46)
        
        # Set x-axis limits to show range from -60 to 600 seconds (-1 to 10 minutes)
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
            ax_new.set_xlabel('Time relative to room temp sensor starting to drop (MM:SS)', fontsize=16, labelpad=10)
        
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
    fig.suptitle('Cooling rate comparison (first %d minutes)' % mins, fontsize=20, weight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

if __name__ == "__main__":
    # # Create the publication-quality plot
    fig = create_cooling_rate_comparison()
    # plt.show()
    #
    # # Save the figure with high resolution for publication
    # print("Saving high-resolution figure for publication...")
    #
    # # Save to the same directory as the script

    # Create and save the 10-minute version
    print("Creating 10-minute version of the figure...")
    fig_10m = create_shorter_version(fig, mins=10)

    print("Creating 2-minute version of the figure...")
    fig_2m = create_shorter_version(fig, mins=2, xmin=35)

    # show
    plt.show()

    # Save the figures
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating.png')
    fig.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"Done! Figure saved as {save_path}")
    save_path_10m = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_10m.png')
    fig_10m.savefig(save_path_10m, dpi=600, bbox_inches='tight')
    print(f"Done! 10-minute version saved as {save_path_10m}")
    save_path_2m = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_2m.png')
    fig_2m.savefig(save_path_2m, dpi=600, bbox_inches='tight')
    print(f"Done! 10-minute version saved as {save_path_10m}")
