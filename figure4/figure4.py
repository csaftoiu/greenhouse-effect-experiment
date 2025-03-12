import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator
from scipy.interpolate import interp1d
from scipy import integrate
import os

# Import local data generation module
from generate_csv_data import generate_all_data

def generate_data_files():
    """
    Generate all necessary data files if they don't exist
    """
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define data directory
    data_dir = os.path.join(script_dir, 'data')
    
    # Generate all necessary CSV data files using the utility function
    generate_all_data(data_dir)
    
    print(f"All necessary data files generated in {data_dir}")

def load_data():
    """
    Load data from CSV files
    """
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    
    # File paths
    bb_path = os.path.join(data_dir, 'blackbody_spectrum.csv')
    boro_path = os.path.join(data_dir, 'borosilicate_transmission.csv')
    caf2_path = os.path.join(data_dir, 'caf2_transmission.csv')
    
    # Check if data files exist, if not generate them
    if not os.path.exists(bb_path) or \
       not os.path.exists(boro_path) or \
       not os.path.exists(caf2_path):
        generate_data_files()
    
    # Load all three datasets
    blackbody_df = pd.read_csv(bb_path)
    boro_df = pd.read_csv(boro_path)
    caf2_df = pd.read_csv(caf2_path)
    
    return blackbody_df, boro_df, caf2_df

def create_combined_plot():
    """
    Create a plot with:
    - X-axis for wavelengths in μm
    - Y-axis for spectral radiance
    - Shaded areas showing transmitted radiation through different materials
    - Calculation of total percentage of radiation transmitted
    """
    # Load data
    blackbody_df, boro_df, caf2_df = load_data()
    
    # Create figure with publication quality settings
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
    
    # Create a figure with the same width but taller to accommodate two plots
    fig = plt.figure(figsize=(10, 8.0))
    
    # Create two subplots stacked on top of each other with shared x-axis
    # For top plot - transmission percentage
    ax1 = fig.add_axes([0.12, 0.58, 0.82, 0.35])
    # For bottom plot - spectral radiance
    ax2 = fig.add_axes([0.12, 0.10, 0.82, 0.33])
    
    # Get blackbody data
    bb_wl = blackbody_df['Wavelength (um)']
    bb_rad = blackbody_df['Spectral Radiance (W/m²/sr/μm)']
    
    # Get raw transmission data for both materials
    boro_wl = boro_df['Wavelength (um)']
    boro_trans_pct = boro_df['Transmission (%)']
    caf2_wl = caf2_df['Wavelength (um)']
    caf2_trans_pct = caf2_df['Transmission (%)']
    
    # Create interpolation functions for both materials
    boro_interp = interp1d(boro_df['Wavelength (um)'], boro_df['Transmission (%)'], 
                         bounds_error=False, fill_value=0)
    caf2_interp = interp1d(caf2_df['Wavelength (um)'], caf2_df['Transmission (%)'], 
                         bounds_error=False, fill_value=0)
    
    # Calculate the transmission at blackbody wavelengths
    boro_trans = boro_interp(bb_wl) / 100.0  # Convert to fraction
    caf2_trans = caf2_interp(bb_wl) / 100.0  # Convert to fraction
    
    # Calculate transmitted radiation for each material
    boro_transmitted = bb_rad * boro_trans
    caf2_transmitted = bb_rad * caf2_trans
    
    # Set temperature in Celsius and convert to Kelvin
    temp_C = 65
    temp_K = temp_C + 273.15
    
    # Calculate total areas (integration) to get percentage transmitted
    # Calculate areas using trapezoidal rule for the displayed range
    range_area = np.trapz(bb_rad, bb_wl)
    boro_area = np.trapz(boro_transmitted, bb_wl)
    caf2_area = np.trapz(caf2_transmitted, bb_wl)
    
    # Calculate total graybody emission using Stefan-Boltzmann law
    stefan_boltzmann = 5.670374419e-8  # W/(m²·K⁴)
    emissivity = 0.9
    total_power = emissivity * stefan_boltzmann * temp_K**4  # W/m²
    
    # Convert our integrated values to total power
    # We need to convert from spectral radiance (W/m²/sr/μm) to power (W/m²)
    # First, multiply by π to integrate over hemisphere (sr)
    # Then account for the wavelength range integration
    range_power = range_area * np.pi
    boro_power = boro_area * np.pi
    caf2_power = caf2_area * np.pi
    
    # Calculate percentages relative to total graybody emission
    boro_percentage = (boro_power / total_power) * 100
    caf2_percentage = (caf2_power / total_power) * 100
    
    # ----- Top Plot: Transmission Percentage -----
    
    # Calculate the scale factor to make peak coincide with 100%
    max_bb_rad = bb_rad.max()
    scale_factor = 100.0 / max_bb_rad
    
    # Scale the graybody curve to the transmission percentage scale (0-100%)
    bb_rad_scaled = bb_rad * scale_factor
    
    # Plot the graybody curve first (to make it first in the legend)
    ax1.plot(bb_wl, bb_rad_scaled, 
            color='#D62728', linewidth=2.0, linestyle='--',
            label=f'Graybody Emission')
    
    # Plot transmission curves
    ax1.plot(caf2_wl, caf2_trans_pct, 
            color='#2CA02C', linewidth=2.5, 
            label='CaF₂ Transmission %')
    ax1.plot(boro_wl, boro_trans_pct, 
            color='#FF8C00', linewidth=2.5, # Bright orange 
            label='Borosilicate Transmission %')
    
    # Set y-axis limits and labels for transmission plot
    ax1.set_ylim(0, 105)
    ax1.set_ylabel('Transmission (%)', fontsize=16, labelpad=10)
    ax1.set_xlabel('Wavelength (μm)', fontsize=16, labelpad=10)
    ax1.set_title(f'Material Transmission vs Graybody ({temp_C}°C, ε=0.9) Emission', fontsize=18, pad=15, weight='bold')
    
    # Set x-axis limits and tick marks for top plot
    ax1.set_xlim(0, 20)
    ax1.xaxis.set_major_locator(MultipleLocator(2))
    ax1.xaxis.set_minor_locator(MultipleLocator(0.5))
    
    # Add grid with improved styling
    ax1.grid(True, linestyle='--', alpha=0.4, linewidth=0.8)
    
    # Create legend for top plot with explicit styling
    legend1 = ax1.legend(
                       loc='upper right', frameon=True, fancybox=True,
                       shadow=True, borderpad=1, labelspacing=0.8)
        # # Style the legend box
    # frame1 = legend1.get_frame()
    # frame1.set_facecolor('white')  # Explicitly set background color
    # frame1.set_alpha(0.9)
    # frame1.set_edgecolor('black')
    # frame1.set_linewidth(1.5)
    
    # ----- Bottom Plot: Spectral Radiance and Transmitted Radiation -----
    
    # Plot graybody spectrum
    ax2.plot(bb_wl, bb_rad, 
             color='#D62728', linewidth=3.0,
             label=f'Graybody Emission')
    
    # Plot the transmission curves with shading
    # First, add CaF2 shading (lower z-order)
    ax2.fill_between(bb_wl, 0, caf2_transmitted, 
                    color='#2CA02C', alpha=0.3, 
                    label='CaF₂ Transmitted', zorder=10)
    
    # Then add borosilicate shading on top (higher z-order)
    ax2.fill_between(bb_wl, 0, boro_transmitted, 
                    color='#FF8C00', alpha=0.5, 
                    label='Borosilicate Transmitted', zorder=20)
    
    # Still keep the lines for better visual clarity
    ax2.plot(bb_wl, caf2_transmitted, 
           color='#2CA02C', linewidth=2.5, 
           label='_nolegend_')  # Hide from legend since shaded area has label
    ax2.plot(bb_wl, boro_transmitted, 
           color='#FF8C00', linewidth=2.5, 
           label='_nolegend_')  # Hide from legend since shaded area has label
    
    # Set y-axis limit with 5% headroom
    max_radiance = bb_rad.max()
    ax2.set_ylim(0, max_radiance * 1.05)
    
    # Add text with total percentages - improved formatting
    textstr = f"Total radiation transmitted:\n" \
              f"Borosilicate Glass: {boro_percentage:.1f}%\n" \
              f"CaF₂: {caf2_percentage:.1f}%"
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, 
                edgecolor='gray', linewidth=1.5, pad=0.8)
    # Position in upper right, below the legend
    ax2.text(0.98, 0.29, textstr, transform=ax2.transAxes, fontsize=14,
            verticalalignment='top', horizontalalignment='right', bbox=props)
    
    # Set labels and title for bottom plot
    ax2.set_xlabel('Wavelength (μm)', fontsize=16, labelpad=10)
    ax2.set_ylabel('Spectral Radiance (W/m²/sr/μm)', fontsize=16, labelpad=10)
    ax2.set_title('Transmission of Graybody Emission', fontsize=18, pad=15, weight='bold')
    
    # Set x-axis limits and tick marks
    ax2.set_xlim(0, 20)
    ax2.xaxis.set_major_locator(MultipleLocator(2))
    ax2.xaxis.set_minor_locator(MultipleLocator(0.5))
    
    ax2.set_ylim(0, 17)
    ax2.yaxis.set_major_locator(MultipleLocator(2))
    ax2.yaxis.set_minor_locator(MultipleLocator(1))

    # Add grid with improved styling
    ax2.grid(True, linestyle='--', alpha=0.4, linewidth=0.8)
    
    # Create legend for right plot
    legend2 = ax2.legend(loc='upper right', frameon=True, fancybox=True,
                       shadow=True, borderpad=1, labelspacing=0.8)
    
    # Add an arrow pointing to the small borosilicate bump around 3 μm
    ax2.annotate('Borosilicate', xy=(3.3, 0.3), xytext=(1.5, 5),
                arrowprops=dict(facecolor='#FF8C00', shrink=0.05, width=2, 
                               headwidth=8, alpha=0.8),
                fontsize=12, color='#FF8C00', fontweight='bold',
                horizontalalignment='left', verticalalignment='center')
    
    return fig


if __name__ == "__main__":
    # Create the combined plot
    fig = create_combined_plot()
    
    # Show the plot
    plt.show()
    
    # Save the plot with high resolution
    import os
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure4.png')
    
    fig.savefig(save_path, dpi=600, bbox_inches='tight')
    print(f"High-resolution plot saved as {save_path}")