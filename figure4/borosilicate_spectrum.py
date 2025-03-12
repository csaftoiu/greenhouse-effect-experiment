import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator

def generate_borosilicate_spectrum():
    """
    Generate the transmission spectrum of borosilicate glass
    
    Returns:
        wavelengths: Array of wavelengths in nm
        transmission: Array of transmission percentages (0-100%)
    """
    # Define key points from the specified values
    key_wavelengths = np.array([
        200,  # 0%
        250,  # 90%
        1200, # 88%
        1700, # 90%
        2100, # 90%
        2200, # 88%
        2700, # 50% (smooth rounded curve endpoint)
        3000, # 25% (bottoms out)
        3200, # 42% (swings back up)
        3700, # 5% (straight line down)
        3800  # 0%
    ])
    
    key_transmissions = np.array([
        0,    # 200nm
        90,   # 250nm
        88,   # 1200nm
        90,   # 1700nm
        90,   # 2100nm
        88,   # 2200nm
        50,   # 2700nm (smooth rounded curve)
        25,   # 3000nm (bottoms out)
        42,   # 3200nm (swings back up)
        5,    # 3700nm (straight line down)
        0     # 3800nm
    ])
    
    # Generate a finer wavelength scale for plotting
    wavelengths = np.linspace(200, 4000, 1000)
    
    # Use PCHIP interpolation for a smooth, natural-looking curve that respects the shape
    interpolator = PchipInterpolator(key_wavelengths, key_transmissions)
    transmission = interpolator(wavelengths)
    
    # Ensure no negative values
    transmission = np.clip(transmission, 0, 100)
    
    return wavelengths, transmission