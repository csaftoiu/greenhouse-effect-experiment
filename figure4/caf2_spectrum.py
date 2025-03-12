import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator

def generate_caf2_spectrum():
    """
    Generate the transmission spectrum of Calcium Fluoride (CaF2)
    
    Returns:
        wavelengths: Array of wavelengths in μm
        transmission: Array of transmission percentages (0-100%)
    """
    # Define key points from the specified values
    key_wavelengths = np.array([
        0.25,  # 90%
        0.5,   # 92%
        4.5,   # 95% (peak of smooth curve)
        7.5,   # 93%
        11.0,  # 5% (bottom of smooth rounded curve)
        12.0,  # 0% (hyperbolic taper)
        20.0   # 0% (ensure it remains 0% beyond 12μm)
    ])
    
    key_transmissions = np.array([
        90,  # 0.25μm
        92,  # 0.5μm
        95,  # 4.5μm (peak)
        93,  # 7.5μm
        5,   # 11.0μm (bottom of rounded curve)
        0,   # 12.0μm (end of hyperbolic taper)
        0    # 20.0μm (ensure it remains 0%)
    ])
    
    # Generate a finer wavelength scale for plotting
    wavelengths = np.linspace(0.2, 20, 1000)
    
    # Use PCHIP interpolation for a smooth, natural-looking curve that respects the shape
    interpolator = PchipInterpolator(key_wavelengths, key_transmissions)
    transmission = interpolator(wavelengths)
    
    # Ensure no negative values and max of 100%
    transmission = np.clip(transmission, 0, 100)
    
    # Force transmission to be exactly 0 after 12μm
    transmission[wavelengths > 12] = 0
    
    return wavelengths, transmission