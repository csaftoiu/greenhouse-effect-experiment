import numpy as np
import matplotlib.pyplot as plt
from scipy import constants
from scipy import integrate
import pandas as pd
import os

# Import our spectrum generation functions
from blackbody import generate_blackbody_spectrum
from borosilicate_spectrum import generate_borosilicate_spectrum
from caf2_spectrum import generate_caf2_spectrum

def save_blackbody_csv(data_dir=None):
    """Generate and save blackbody spectrum data to CSV"""
    # Set default data directory to current directory if not specified
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate blackbody spectrum for T=65°C (338.15K)
    temp_C = 65
    temp_K = temp_C + 273.15
    wavelengths_um, radiance = generate_blackbody_spectrum(0.1, 20, 1000, temp_K, 0.9)
    
    # Convert wavelengths to nm
    wavelengths_nm = wavelengths_um * 1000
    
    # Create dataframe
    df = pd.DataFrame({
        'Wavelength (um)': wavelengths_um,
        'Spectral Radiance (W/m²/sr/μm)': radiance
    })
    
    # Save to CSV
    csv_path = os.path.join(data_dir, 'blackbody_spectrum.csv')
    df.to_csv(csv_path, index=False)
    print(f"Saved blackbody spectrum to {csv_path}")
    
    return csv_path

def save_borosilicate_csv(data_dir=None):
    """Generate and save borosilicate glass transmission data to CSV"""
    # Set default data directory to current directory if not specified
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate borosilicate spectrum
    wavelengths_nm, transmission = generate_borosilicate_spectrum()
    
    # Convert wavelengths to um
    wavelengths_um = wavelengths_nm / 1000
    
    # Create dataframe
    df = pd.DataFrame({
        'Wavelength (um)': wavelengths_um,
        'Transmission (%)': transmission
    })
    
    # Save to CSV
    csv_path = os.path.join(data_dir, 'borosilicate_transmission.csv')
    df.to_csv(csv_path, index=False)
    print(f"Saved borosilicate transmission to {csv_path}")
    
    return csv_path

def save_caf2_csv(data_dir=None):
    """Generate and save calcium fluoride (CaF2) transmission data to CSV"""
    # Set default data directory to current directory if not specified
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate CaF2 spectrum
    wavelengths_um, transmission = generate_caf2_spectrum()
    
    # Create dataframe
    df = pd.DataFrame({
        'Wavelength (um)': wavelengths_um,
        'Transmission (%)': transmission
    })
    
    # Save to CSV
    csv_path = os.path.join(data_dir, 'caf2_transmission.csv')
    df.to_csv(csv_path, index=False)
    print(f"Saved CaF2 transmission to {csv_path}")
    
    return csv_path

def generate_all_data(data_dir=None):
    """Generate all CSV files needed for the figure"""
    # Set default data directory to current directory if not specified
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate all three CSV files
    save_blackbody_csv(data_dir)
    save_borosilicate_csv(data_dir)
    save_caf2_csv(data_dir)
    
    print(f"All CSV files generated successfully in {data_dir}")

if __name__ == "__main__":
    # Generate all three CSV files in the default location
    generate_all_data()