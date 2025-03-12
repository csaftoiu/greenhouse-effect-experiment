import numpy as np
import matplotlib.pyplot as plt
from scipy import constants
from scipy import integrate
import pandas as pd

def generate_blackbody_spectrum(wavelength_min, wavelength_max, num_points, temperature, emissivity=1.0):
    """
    Generate blackbody spectrum data.
    
    Args:
        wavelength_min: Minimum wavelength in microns
        wavelength_max: Maximum wavelength in microns
        num_points: Number of points to generate
        temperature: Temperature in Kelvin
        emissivity: Emissivity factor (default 1.0)
        
    Returns:
        wavelengths: Array of wavelengths in microns
        spectral_radiance: Array of spectral radiance values (W/m²/sr/μm)
    """
    # Ensure minimum wavelength is not zero to avoid division by zero
    if wavelength_min <= 0:
        wavelength_min = 0.1  # Set a small positive number
        
    # Convert wavelength from microns to meters
    wavelengths = np.linspace(wavelength_min, wavelength_max, num_points)
    wavelengths_m = wavelengths * 1e-6
    
    # Constants
    h = constants.h  # Planck's constant
    c = constants.c  # Speed of light
    k = constants.k  # Boltzmann constant
    
    # Planck's law formula
    # Simplified to return spectral radiance in W/m²/sr/μm
    numerator = 2.0 * h * c**2
    denominator = wavelengths_m**5 * (np.exp(h*c/(wavelengths_m*k*temperature)) - 1.0)
    spectral_radiance = emissivity * numerator / denominator
    
    # Convert from W/m²/sr/m to W/m²/sr/μm (multiply by 1e-6)
    spectral_radiance = spectral_radiance * 1e-6
    
    return wavelengths, spectral_radiance