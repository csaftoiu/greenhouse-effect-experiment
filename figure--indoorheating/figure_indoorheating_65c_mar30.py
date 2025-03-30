import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import numpy as np
import os
from utils import set_plot_style, format_time, load_dataset, filter_time_periods, adjust_color, create_shorter_version

def create_cooling_rate_comparison():
    """
    Creates a publication-quality plot comparing cooling rates for different
    configurations: CAF2 and BORO, using the Mar30 panel heater data.
    """
    # Set publication-quality style parameters
    set_plot_style()

    # Load data
    print("Loading data...")
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Load Mar30 data
    csv_fn = os.path.join(data_dir, 'indoor_heating_data_mar30_65_panelater.csv')
    data = load_dataset(csv_fn)

    # Define columns based on header information
    temp_columns = data.columns[2:6]  # Temperature columns
    print(f"Temperature columns: {temp_columns}")

    # Define sensor names from the second row of the file
    sensor_names = ["Air near apparatus", "top pane topside", "black bottom", "apparatus bottom"]
    
    # Define time periods to extract with the specified time ranges
    time_periods = {
        'CAF2': {
            'start': '2025-03-30 13:51:48',
            'end': '2025-03-30 14:27:25',
            'data': data
        },
        'BORO': {
            'start': '2025-03-30 12:09:52',
            'end': '2025-03-30 13:07:10',
            'data': data
        }
    }
    start_offset = 120

    # Filter data for each time period
    period_data = filter_time_periods(time_periods, start_offset=start_offset)
    
    # Define color base for each temperature column
    base_colors = {
        temp_columns[0]: '#00FFFF',  # Air near apparatus - Cyan
        temp_columns[1]: '#00FF00',  # Top pane topside - Green
        temp_columns[2]: '#FF0000',  # Black bottom - Red
        temp_columns[3]: '#808080',  # Apparatus bottom - Gray
    }
    
    # Define line styles for each period
    period_line_styles = {
        'CAF2': '--',   # Dashed (like CAF2)
        'BORO': '-',    # Solid (like BORO)
    }
    
    # Define darkness levels for each period
    darkness_levels = {
        'CAF2': 1.25,   # Darker than CAF2
        'BORO': 1.25,   # Darker than BORO
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
        ordered_periods = ['CAF2', 'BORO']
        
        # Loop through each time period in the specified order
        for i, period_name in enumerate(ordered_periods):
            # Get the dataframe for this period
            if period_name in period_data:
                df = period_data[period_name]
                
                # Filter data to the time range we want to display
                df_filtered = df[(df['seconds'] >= min_seconds) & (df['seconds'] <= max_seconds)]
                
                # Get color for this sensor and adjust based on darkness level
                base_color = base_colors[col]
                color = adjust_color(base_color, darkness_levels[period_name], col, period_name, temp_columns)
                
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
        ax.xaxis.set_major_formatter(plt.FuncFormatter(format_time))
        ax.xaxis.set_major_locator(mticker.MultipleLocator(600))  # Every 10 minutes
        ax.xaxis.set_minor_locator(mticker.MultipleLocator(60))   # Every minute
        
        # Set y-axis ticks
        ax.yaxis.set_major_locator(mticker.MultipleLocator(5))    # Every 5°C
        ax.yaxis.set_minor_locator(mticker.MultipleLocator(1))    # Every 1°C
    
    # Add a global title for the entire figure
    fig.suptitle('Cooling rate comparison - 65°C Panel Heater (Mar 30)', fontsize=20, weight='bold', y=0.98)
    
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
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_65c_mar30.png')
    fig.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"Done! Figure saved as {save_path}")
    save_path_10m = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_65c_mar30_10m.png')
    fig_10m.savefig(save_path_10m, dpi=600, bbox_inches='tight')
    print(f"Done! 10-minute version saved as {save_path_10m}")
    save_path_2m = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure_indoorheating_65c_mar30_2m.png')
    fig_2m.savefig(save_path_2m, dpi=600, bbox_inches='tight')
    print(f"Done! 2-minute version saved as {save_path_2m}")