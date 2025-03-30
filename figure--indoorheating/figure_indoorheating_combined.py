import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import numpy as np
import os

from utils import (
    set_plot_style, format_time, load_dataset, filter_time_periods,
    adjust_color, create_shorter_version
)

# Target temperature for alignment in the original dataset
TARGET_TEMP = 44.3

def create_combined_cooling_comparison():
    """
    Creates a publication-quality plot combining both the original dataset and
    the 65C dataset for direct comparison.
    """
    # Set publication-quality style parameters
    set_plot_style()

    # Load all data files
    print("Loading data...")
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Load original data
    csv_fn = os.path.join(data_dir, 'indoor_heating_data.csv')
    data = load_dataset(csv_fn, "original")
    
    # Load Mar29 data
    csv_fn_mar29 = os.path.join(data_dir, 'indoor_heating_data_mar29.csv')
    data_mar29 = load_dataset(csv_fn_mar29, "Mar29")
    
    # Load Mar29 65C run data
    csv_fn_mar29_65c = os.path.join(data_dir, 'indoor_heating_data_mar29_run65.csv')
    data_mar29_65c = load_dataset(csv_fn_mar29_65c, "Mar29 65C")
    
    # Load Mar29 65C v2 run data (for the new CAF2x4 data)
    csv_fn_mar29_65c_v2 = os.path.join(data_dir, 'indoor_heating_data_mar29_run65_v2.csv')
    data_mar29_65c_v2 = load_dataset(csv_fn_mar29_65c_v2, "Mar29 65C v2")

    # Define columns based on header information - should be the same for all datasets
    temp_columns = data.columns[2:6]  # Temperature columns
    print(f"Temperature columns: {temp_columns}")

    # Define sensor names from the second row of the file
    sensor_names = ["Air near apparatus", "top pane topside", "black bottom", "apparatus bottom"]
    
    # Define the index of the apparatus bottom sensor column for alignment
    apparatus_bottom_col = temp_columns[3]

    # Define time periods to extract (as specified in the requirements)
    # Original data with temperature alignment
    original_time_periods = {
        'NOPANE': {
            'start': '2025-03-28 17:02:54',
            'end': '2025-03-28 17:34:16',
            'data': data
        },
        'CAF2': {
            'start': '2025-03-28 18:27:27',
            'end': '2025-03-28 19:29:00',
            'data': data
        },
        'BORO': {
            'start': '2025-03-28 20:05:19',
            'end': '2025-03-28 20:59:34',
            'data': data
        },
        'BOROx4': {
            'start': '2025-03-29 11:04:02',
            'end': '2025-03-29 12:25:42',
            'data': data_mar29
        },
        'CAF2x4': {
            'start': '2025-03-29 13:42:46',
            'end': '2025-03-29 15:04:00',
            'data': data_mar29
        }
    }
    
    # 65C data without temperature alignment
    data_65c_time_periods = {
        'CAF2x4_65c': {
            'start': '2025-03-29 21:03:41',
            'end': '2025-03-29 21:32:00',
            'data': data_mar29_65c_v2
        },
        'BOROx4_65c': {
            'start': '2025-03-29 18:44:03',
            'end': '2025-03-29 19:15:49',
            'data': data_mar29_65c
        }
    }
    
    # Process both datasets
    start_offset = 120
    
    # Original data with temperature alignment
    period_data_original = filter_time_periods(
        original_time_periods, 
        start_offset=start_offset,
        align_to_temp=True,
        target_temp=TARGET_TEMP,
        apparatus_bottom_col=apparatus_bottom_col
    )
    
    # 65C data without temperature alignment
    period_data_65c = filter_time_periods(
        data_65c_time_periods, 
        start_offset=start_offset,
        align_to_temp=False
    )
    
    # Combine the data dictionaries
    period_data = {**period_data_original, **period_data_65c}
    
    # Define color base for each temperature column
    base_colors = {
        temp_columns[0]: '#00FFFF',  # Air near apparatus - Cyan
        temp_columns[1]: '#00FF00',  # Top pane topside - Green
        temp_columns[2]: '#FF0000',  # Black bottom - Red
        temp_columns[3]: '#808080',  # Apparatus bottom - Gray
    }
    
    # Define line styles for each period
    period_line_styles = {
        'NOPANE': ':',    # Dotted
        'CAF2': '--',     # Dashed
        'BORO': '-',      # Solid
        'BOROx4': '-',    # Solid (like BORO)
        'CAF2x4': '--',   # Dashed (like CAF2)
        'CAF2x4_65c': '--',   # Dashed (like CAF2)
        'BOROx4_65c': '-',    # Solid (like BORO)
    }
    
    # Define darkness levels for each period
    darkness_levels = {
        'NOPANE': 0.5,    # Lighter
        'CAF2': 0.75,     # Medium
        'BORO': 1.0,      # Darker
        'BOROx4': 1.25,   # Darker than BORO
        'CAF2x4': 1.25,   # Darker than CAF2
        'BOROx4_65c': 1.5,   # Even darker than BOROx4
        'CAF2x4_65c': 1.5,   # Even darker than CAF2x4
    }
    
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
        ordered_periods = ['NOPANE', 'CAF2', 'CAF2x4', 'CAF2x4_65c', 'BORO', 'BOROx4', 'BOROx4_65c']
        
        # Loop through each time period in the specified order
        for i, period_name in enumerate(ordered_periods):
            # Get the dataframe for this period
            if period_name in period_data:
                df = period_data[period_name]
                
                # Filter data to the time range we want to display
                df_filtered = df[(df['seconds'] >= min_seconds) & (df['seconds'] <= max_seconds)]
                
                # Get color for this sensor and adjust based on darkness level
                base_color = base_colors[col]
                color = adjust_color(
                    base_color, 
                    darkness_levels[period_name], 
                    col, 
                    period_name,
                    temp_columns
                )
                
                # Create label with prefix based on period and dataset
                if period_name.endswith('_65c'):
                    label = f"{period_name[:-4]} (65°C)"
                else:
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
            ax.set_xlabel('Time (MM:SS)', fontsize=16, labelpad=10)
        
        # Only add y-label to leftmost subplots
        if j % 2 == 0:
            ax.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)
        
        # Configure tick formatting
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_time))
        ax.xaxis.set_major_locator(mticker.MultipleLocator(600))  # Every 10 minutes
        ax.xaxis.set_minor_locator(mticker.MultipleLocator(60))   # Every minute
        
        # Set y-axis ticks
        ax.yaxis.set_major_locator(mticker.MultipleLocator(5))    # Every 5°C
        ax.yaxis.set_minor_locator(mticker.MultipleLocator(1))    # Every 1°C
    
    # Add a global title for the entire figure
    fig.suptitle('Combined Cooling Rate Comparison', fontsize=20, weight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def create_65c_focused_version(original_fig, mins_start=0, mins_end=8, ymin=53, ymax=65):
    """
    Create a focused version that shows only the 65C data in a specific time and temperature range
    """
    # Create a new figure
    fig = plt.figure(figsize=(16, 12))
    
    # Parse times for interpolation
    import pandas as pd
    start_time = pd.to_datetime('2025-03-29 16:39:59')  # CAF2x4 start time
    interp_start_time = pd.to_datetime('2025-03-29 16:40:01')  # Interpolation start time
    interp_end_time = pd.to_datetime('2025-03-29 16:40:27')  # Interpolation end time
    
    # Calculate seconds for interpolation
    start_seconds = (interp_start_time - start_time).total_seconds()
    end_seconds = (interp_end_time - start_time).total_seconds()
    
    # Copy the subplots from the original figure
    for i, ax_orig in enumerate(original_fig.axes):
        # Create a new subplot
        ax_new = fig.add_subplot(2, 2, i+1)
        
        # Copy only the 65C data lines from original axis to new axis
        for line in ax_orig.lines:
            label = line.get_label()
            # Only include 65C datasets
            if '65°C' in label:
                # Get the data
                x_data = line.get_xdata()
                y_data = line.get_ydata()
                
                # Filter data to include from -30 seconds to the specified end time
                mask = (x_data >= -30) & (x_data <= mins_end*60)
                x_filtered = x_data[mask]
                y_filtered = y_data[mask]
                
                # Plot the filtered data on the new axis
                ax_new.plot(
                    x_filtered, 
                    y_filtered,
                    label=label,
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
        if i == 1:  # For top pane topside subplot
            ax_new.set_ylim(39, ymax)
        else:
            ax_new.set_ylim(ymin, ymax)
        
        # Set x-axis limits to start at -30 seconds instead of 0
        ax_new.set_xlim(-30, mins_end*60)
        
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
        ax_new.xaxis.set_major_formatter(plt.FuncFormatter(format_time))
        ax_new.xaxis.set_major_locator(mticker.MultipleLocator(60))   # Every minute
        ax_new.xaxis.set_minor_locator(mticker.MultipleLocator(15))   # Every 15 seconds
        
        # Set y-axis ticks
        ax_new.yaxis.set_major_locator(mticker.MultipleLocator(2))    # Every 2°C
        ax_new.yaxis.set_minor_locator(mticker.MultipleLocator(0.5))  # Every 0.5°C
        
        # Add vertical line
        divergence_time = 45
        ax_new.axvline(x=divergence_time, color='purple', linestyle='--', linewidth=1.5, 
                      label='Top pane divergence' if i == 1 else '_nolegend_')
        
        # Add text annotation on the top pane plot (subplot 1) and black bottom plot (subplot 2)
        if i == 1:
            ax_new.text(divergence_time + 5, 62, 'Top pane temps\ndiverge here', 
                      color='purple', fontsize=10, ha='left', va='top')
        elif i == 2:
            ax_new.text(divergence_time + 5, 54, 'Top pane temps\ndiverge here', 
                      color='purple', fontsize=10, ha='left', va='bottom')
    
    # Add a global title
    fig.suptitle('65°C Run Cooling Rate (Minutes -0.5-%d, %d-%d°C)' % 
                (mins_end, ymin, ymax), 
                fontsize=20, weight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

if __name__ == "__main__":
    import sys
    
    # Check for command line argument
    if len(sys.argv) > 1 and sys.argv[1] == "65c-focused":
        # Create the publication-quality plot first (needed for all versions)
        print("Generating base plot...")
        fig = create_combined_cooling_comparison()
        
        # Create the 65C focused version
        print("Creating 65°C focused version (minutes 0-8, 53-65°C)...")
        fig_65c_focused = create_65c_focused_version(fig, mins_start=0, mins_end=8, ymin=53, ymax=65)
        
        # Save the focused version
        save_path_65c_focused = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                          'figure_indoorheating_65c_focused.png')
        fig_65c_focused.savefig(save_path_65c_focused, dpi=600, bbox_inches='tight')
        print(f"Done! 65°C focused version saved as {save_path_65c_focused}")
        
        # Show the focused version
        plt.show()
    else:
        # Create the publication-quality plot
        fig = create_combined_cooling_comparison()
        
        # Create and save the 10-minute version
        print("Creating 10-minute version of the figure...")
        fig_10m = create_shorter_version(
            fig, 
            mins=10,
            figure_title='Combined Cooling Rate Comparison (first %d minutes)'
        )

        print("Creating 2-minute version of the figure...")
        fig_2m = create_shorter_version(
            fig, 
            mins=2, 
            xmin=35,
            figure_title='Combined Cooling Rate Comparison (first %d minutes)'
        )

        # Show figures
        plt.show()

        # Save the figures
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_combined.png')
        fig.savefig(save_path, dpi=600, bbox_inches='tight')
        print(f"Done! Figure saved as {save_path}")
        
        save_path_10m = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_combined_10m.png')
        fig_10m.savefig(save_path_10m, dpi=600, bbox_inches='tight')
        print(f"Done! 10-minute version saved as {save_path_10m}")
        
        save_path_2m = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_combined_2m.png')
        fig_2m.savefig(save_path_2m, dpi=600, bbox_inches='tight')
        print(f"Done! 2-minute version saved as {save_path_2m}")