import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

def create_figure2():
    """
    Creates Figure 2 - Temperature vs. Insolation by Pane Configuration.
    """
    # Set publication-quality parameters
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'mathtext.fontset': 'stix',
        'font.size': 9,
        'axes.labelsize': 10,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 8,
        'figure.dpi': 300,
        'savefig.dpi': 600,
        'figure.figsize': (3.5, 2.8),  # Journal column width
        'axes.linewidth': 0.5,
        'grid.linewidth': 0.5,
        'lines.linewidth': 1.0,
        'lines.markersize': 4,
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'xtick.minor.width': 0.5,
        'ytick.minor.width': 0.5,
    })

    # Data from the table for selected geometries
    geometries = ["----", "CCCC", "BCCC", "BBCC", "BBBB"]
    peak_temps = [64.5, 69.4, 74.7, 77.1, 79.2]
    peak_temp_errors = [0.1, 0.1, 0.1, 0.1, 0.1]
    ins_bottom = [881, 755, 716, 726, 733]
    ins_bottom_errors = [10.7, 18.5, 15.6, 15.5, 16.1]
    ins_top = [943, 948, 912, 929, 924]  # Adding insolation top data
    ins_top_errors = [2.5, 1.5, 3.5, 2.0, 6.0]  # Adding insolation top errors

    # Save data to CSV for reference
    import pandas as pd
    data_df = pd.DataFrame({
        'Configuration': geometries,
        'Peak_Temperature': peak_temps,
        'Peak_Temperature_Error': peak_temp_errors,
        'Insolation_Bottom': ins_bottom,
        'Insolation_Bottom_Error': ins_bottom_errors,
        'Insolation_Top': ins_top,
        'Insolation_Top_Error': ins_top_errors
    })
    # Get script directory and ensure data directory exists
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to figure2/data directory
    data_path = os.path.join(data_dir, 'figure3b_data.csv')
    data_df.to_csv(data_path, index=False)
    print(f"Saved figure data to {data_path}")

    # Set colors for bottom and top insolation
    bottom_color = '#1f77b4'  # Blue for bottom insolation
    top_color = '#ff7f0e'     # Orange for top insolation

    # Use circles for all data points
    marker = 'o'

    # Create figure
    fig, ax = plt.subplots()

    # Format labels for legend
    formats = {
        "----": "Uncovered",
        "CCCC": "CCCC",
        "BCCC": "BCCC",
        "BBCC": "BBCC",
        "BBBB": "BBBB"
    }

    # Create scatter plots with error bars for both insolation bottom and top
    bottom_points = []
    top_points = []

    for i, geo in enumerate(geometries):
        # Get formatted label for legend
        formatted_geo = formats[geo]
        
        # Draw bottom insolation data point with error bars
        bottom = ax.errorbar(
            peak_temps[i], 
            ins_bottom[i], 
            xerr=peak_temp_errors[i], 
            yerr=ins_bottom_errors[i], 
            fmt=marker, 
            capsize=3,
            color=bottom_color,
            elinewidth=0.8,
            markeredgewidth=0.8,
            markeredgecolor='black',
            markersize=6,
            zorder=3,
            label=formatted_geo if i == 0 else ""
        )
        
        # Draw top insolation data point with error bars
        top = ax.errorbar(
            peak_temps[i], 
            ins_top[i], 
            xerr=peak_temp_errors[i], 
            yerr=ins_top_errors[i], 
            fmt=marker, 
            capsize=3,
            color=top_color,
            elinewidth=0.8,
            markeredgewidth=0.8,
            markeredgecolor='black',
            markersize=6,
            zorder=3
        )
        
        if i == 0:
            bottom_points.append(bottom)
            top_points.append(top)
        
        # Add configuration labels directly on the plot
        if geo == "----":
            # Put "Uncovered" below with the left edge aligned with the data point
            ax.text(peak_temps[i]-0.25, ins_bottom[i]+9.5, "Uncovered",
                    fontsize=7, ha='left', va='bottom', color='black', fontweight='bold')
        else:
            # Put config code above the data points
            ax.text(peak_temps[i], ins_bottom[i]+18, geo, 
                    fontsize=7, ha='center', va='bottom', color='black', fontweight='bold')

    # Configure axes
    ax.set_xlabel('Peak Temperature (°C)')
    ax.set_ylabel('Insolation (W/m²)')
    ax.set_title('Temperature vs. Insolation by Pane Configuration', pad=8, fontsize=10)

    # Add grid and customize appearance
    ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5, zorder=1)

    # Set axes limits with padding
    ax.set_xlim(64, 80)
    ax.set_ylim(700, 1020)  # Added 50 W/m² padding on top

    # Customize ticks
    ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(4))
    ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(50))
    ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(10))
    ax.tick_params(which='major', length=4, width=0.5)
    ax.tick_params(which='minor', length=2, width=0.5)

    # Create custom legend
    # First for insolation type (bottom vs top)
    insolation_legend = ax.legend(
        [top_points[0], bottom_points[0]],
        ['Total Insolation', 'Insolation Reaching Bottom'],
        loc='upper right',
        fontsize=7,
        frameon=True,
        framealpha=0.8,
        edgecolor='lightgray'
    )

    # Add legend to the plot
    ax.add_artist(insolation_legend)

    # Add simple legend line at the bottom of the plot
    plt.figtext(0.5, 0.01, "B = Borosilicate        C = Calcium Fluoride",
                ha='center', fontsize=7, style='italic')

    # Adjust spacing - very important for publication quality
    plt.tight_layout(pad=0.6)

    # Leave extra space at the bottom for the legends
    plt.subplots_adjust(bottom=0.18)

    # Save figure in high resolution
    save_path = os.path.join(script_dir, 'figure3b.png')
    
    plt.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"Saved figure as {save_path}")

    return fig

if __name__ == "__main__":
    # Create and display Figure 2
    fig = create_figure2()
    plt.show()