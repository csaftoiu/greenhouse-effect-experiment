import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import numpy as np
import os 


def create_publication_quality_plot():
    """
    Creates a publication-quality plot of the trials_repl temperature data
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
    csv_fn = os.path.join(data_dir, 'trials_repl.csv')
    data = pd.read_csv(csv_fn, skiprows=3, encoding='latin1')
    print(f"Loaded {len(data)} rows of data")

    # Convert datetime to proper format
    data['Datetime'] = pd.to_datetime(data.iloc[:, 0])
    print(f"First timestamp: {data['Datetime'].iloc[0]}")
    print(f"Last timestamp: {data['Datetime'].iloc[-1]}")
    
    # Define columns
    temp_columns = data.columns[2:6]  # Temperature columns
    solar_column = data.columns[6]    # Solar insolation column
    
    # Calculate experiment time range
    experiment_start = data['Datetime'].min()
    experiment_end = data['Datetime'].max()
    experiment_duration = (experiment_end - experiment_start).total_seconds() / 60
    print(f"Experiment duration: {experiment_duration:.1f} minutes")
    
    # Load annotations
    annotations_fn = os.path.join(data_dir, 'trials_repl_annotations.csv')
    annotations = pd.read_csv(annotations_fn)
    print(f"Loaded {len(annotations)} configuration annotations")
    
    # Convert annotation times to datetime objects
    experiment_date = experiment_start.date()
    
    # Create a list of dictionaries for annotations with start and end times
    anno_list = []
    for i in range(len(annotations)):
        config = annotations.iloc[i]['geometry']
        time_str = annotations.iloc[i]['time']
        
        # Convert time string to datetime
        time_obj = pd.to_datetime(f"{experiment_date} {time_str}")
        
        # For all except the last one, end time is the start of the next one
        if i < len(annotations) - 1:
            next_time_str = annotations.iloc[i+1]['time']
            end_time = pd.to_datetime(f"{experiment_date} {next_time_str}")
        else:
            # For the last configuration, end time is the experiment end
            end_time = experiment_end
        
        anno_list.append({
            "config": config,
            "start_time": time_obj,
            "end_time": end_time,
            "description": f"Configuration: {config}"
        })
        print(f"Added annotation: {config} from {time_obj.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")
    
    # Create the figure with primary and secondary axes
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_axes([0.12, 0.15, 0.82, 0.75])
    
    # Create secondary axis for solar insolation
    ax2 = ax.twinx()
    
    # Define labels and styling
    temp_labels = ['Black Bottom', 'Bottom Pane Underside', 'Top Pane Topside', 'Apparatus Underside']
    temp_colors = ['#d62728', '#2ca02c', '#8c564b', '#9467bd']  # Red, green, brown, purple (matches figure1)
    temp_linewidths = [3.5, 2, 2, 2]  # Make black bottom extra bold
    temp_linestyles = ['-', '-', '-', '-']
    
    # Solar insolation styling
    solar_color = '#FFD700'  # Bright gold/yellow for solar data
    solar_linewidth = 1.5
    solar_alpha = 1.0  # Full opacity for better visibility
    
    # First plot Black Bottom (index 2 in data, index 0 in labels) with a dark border
    bb_column = temp_columns[2]  # "black bottom" column in data
    
    # First plot a slightly thicker black line as border
    ax.plot(data['Datetime'], data[bb_column].astype(float), 
           color='black',  # Black border
           linewidth=temp_linewidths[0] + 1.5,  # Thicker for border
           linestyle=temp_linestyles[0],
           zorder=20)  # Very high zorder to be on top of everything
           
    # Then plot the red line on top
    ax.plot(data['Datetime'], data[bb_column].astype(float), 
           label=temp_labels[0],  # "Black Bottom" label
           color=temp_colors[0],  # Red
           linewidth=temp_linewidths[0],
           linestyle=temp_linestyles[0],
           zorder=21)  # Even higher zorder to be on top of the border
    
    # Plot the rest of the temperature data
    # Under first glass -> Bottom Pane Underside
    ax.plot(data['Datetime'], data[temp_columns[1]].astype(float), 
           label=temp_labels[1],  # "Bottom Pane Underside" label
           color=temp_colors[1],  # Green
           linewidth=temp_linewidths[1],
           linestyle=temp_linestyles[1])
    
    # Above last glass -> Above Last Pane (with distinct color)
    ax.plot(data['Datetime'], data[temp_columns[0]].astype(float), 
           label=temp_labels[2],  # "Above Last Pane" label
           color=temp_colors[2],  # Brown
           linewidth=temp_linewidths[2],
           linestyle=temp_linestyles[2])
    
    # Underside bottom -> Apparatus Underside
    ax.plot(data['Datetime'], data[temp_columns[3]].astype(float), 
           label=temp_labels[3],  # "Apparatus Underside" label
           color=temp_colors[3],  # Blue
           linewidth=temp_linewidths[3],
           linestyle=temp_linestyles[3])
    
    # Filter solar insolation data - exclude values below 700 W/m² before 15:00
    cutoff_time = pd.to_datetime(f"{experiment_start.date()} 15:00:00")
    solar_data = data.copy()
    
    # Create mask for points to exclude
    before_cutoff = solar_data['Datetime'] < cutoff_time
    low_insolation = solar_data[solar_column].astype(float) < 700
    mask = before_cutoff & low_insolation
    
    # Set these points to NaN to exclude them from plot
    solar_data.loc[mask, solar_column] = np.nan
    
    # Plot solar insolation on secondary axis with a darker border
    # First plot a slightly thicker line with the darker color
    darker_color = '#B8860B'  # Dark goldenrod for the border
    ax2.plot(solar_data['Datetime'], solar_data[solar_column].astype(float),
            color=darker_color,
            linewidth=solar_linewidth + 1.0,  # Slightly thicker
            alpha=solar_alpha,
            linestyle='-',
            zorder=1)  # Lower zorder to be at the back
            
    # Then plot the bright yellow line on top of it
    ax2.plot(solar_data['Datetime'], solar_data[solar_column].astype(float),
            label='Solar Insolation', 
            color=solar_color,
            linewidth=solar_linewidth,
            alpha=solar_alpha,
            linestyle='-',
            zorder=2)  # Low zorder to ensure it's behind temperature lines
    
    # make blackbottom line ordered on top of the ax2
    ax.set_zorder(ax2.get_zorder() - 1)

    # Color mapping function
    def get_config_color(config):
        # Special case for BBBB to match figure1.py exactly
        if config == 'BBBB':
            return '#fdbf6f'  # Light orange for black configuration (from figure1.py)
        
        # Count occurrences of 'C' and 'B'
        c_count = config.count('C')
        b_count = config.count('B')
        
        if config == '----':
            return '#e0e0e0'  # Light gray for empty
        elif b_count == 0:
            # C only configurations - blue gradient
            intensity = c_count / 4  # Normalize to [0,1]
            return plt.cm.Blues(0.3 + 0.5 * intensity)
        else:
            # B configurations - orange gradient
            intensity = b_count / 4  # Normalize to [0,1]
            # Use figure1 BBBB color as the base with varying intensity
            base_color = '#fdbf6f'
            return plt.cm.Oranges(0.3 + 0.5 * intensity)
    
    # Find the end of the last BBBB section first
    bbbb_end_time = None
    for anno in reversed(anno_list):
        if anno["config"] == "BBBB":
            bbbb_end_time = anno["end_time"]
            break
            
    # If found, use as end time, otherwise use 17:15
    if bbbb_end_time:
        plot_end_time = bbbb_end_time
    else:
        plot_end_time = pd.to_datetime(f"{experiment_start.date()} 17:15")
    
    # Add shaded regions for configurations
    for i, anno in enumerate(anno_list):
        config = anno["config"]
        start_time = anno["start_time"]
        end_time = anno["end_time"]
        
        # Skip labels for regions that are completely outside the plot range
        if start_time > plot_end_time:
            continue
            
        # Get color based on configuration
        color = get_config_color(config)
        
        # Add shaded region (only if at least partially visible)
        ax.axvspan(start_time, min(end_time, plot_end_time), alpha=0.35, color=color, zorder=1)
        
        # Add vertical line to distinguish configuration changes (except at start)
        if i > 0:
            ax.axvline(start_time, color='gray', linestyle='--', linewidth=1, alpha=0.7)
        
        # Add configuration label (only if fully within the plot range)
        mid_point = start_time + (end_time - start_time) / 2
        
        # Skip labels that would be cut off or for regions after the plot end
        if mid_point > plot_end_time:
            continue
            
        # Position text label
        ax.text(mid_point, 85, config, 
                horizontalalignment='center', fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', 
                          boxstyle='round,pad=0.5'))
    
    # Temperature axis formatting
    ax.set_title('Thermal Response in Experimental Apparatus Configurations', fontsize=18, weight='bold', pad=15)
    ax.set_xlabel('Time (HH:MM)', fontsize=16, labelpad=10)
    ax.set_ylabel('Temperature (°C)', fontsize=16, labelpad=10)
    
    # Solar insolation axis formatting
    ax2.set_ylabel('Solar Insolation (W/m²)', fontsize=16, labelpad=15, color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # Format x-axis with enhanced time display
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[15, 30, 45]))
    
    # We already found plot_end_time earlier
    # Set x-axis limits
    ax.set_xlim(experiment_start, plot_end_time)
    
    # Set fixed temperature y-axis from 20C to 90C
    ax.set_ylim(20, 90)  # Fixed range as requested
    
    # Set fixed tick intervals for temperature
    temp_major_interval = 10  # 10C intervals for major ticks
    temp_minor_interval = 5   # 5C intervals for minor ticks
    ax.yaxis.set_major_locator(mticker.MultipleLocator(temp_major_interval))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(temp_minor_interval))
    
    # Solar y-axis range and ticks with fixed mapping
    # Map temperature 30°C to 0 W/m² and 85°C to 1200 W/m²
    temp_min_for_mapping = 30
    temp_max_for_mapping = 85
    solar_min_for_mapping = 0
    solar_max_for_mapping = 1200
    
    # Calculate scaling factor
    temp_range_for_mapping = temp_max_for_mapping - temp_min_for_mapping
    solar_range_for_mapping = solar_max_for_mapping - solar_min_for_mapping
    
    # Set fixed y-limits for solar axis
    ax2.set_ylim(solar_min_for_mapping, solar_max_for_mapping)
    
    # Set up evenly spaced ticks at 200 W/m² intervals
    solar_tick_interval = 200
    ax2.yaxis.set_major_locator(mticker.MultipleLocator(solar_tick_interval))
    
    # Combine legends
    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    
    # Combine handles and labels
    all_handles = handles1 + handles2
    all_labels = labels1 + labels2
    
    # Create combined legend at bottom center
    combined_legend = ax.legend(all_handles, all_labels, 
                             loc='lower center', 
                             frameon=True, 
                             fancybox=True,
                             shadow=True, 
                             borderpad=1, 
                             labelspacing=0.8)
    combined_legend.get_frame().set_linewidth(1.5)
    
    # Remove the separate solar legend if it exists
    if ax2.get_legend() is not None:
        ax2.get_legend().remove()
    
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
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure-sep13exp.png')
    
    fig.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"Done! Figure saved as {save_path}")