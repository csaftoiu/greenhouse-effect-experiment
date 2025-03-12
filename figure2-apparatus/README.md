# 2D Apparatus Visualization

This directory contains code to generate a 2D cross-section visualization of the experimental apparatus using Matplotlib.

## Description

The apparatus consists of:
- Multiple cork layers (9cm diameter with 4cm holes)
- 4 removable glass panes (5cm diameter, 2mm thick)
- A special "black bottom" cork layer (painted black)
- Thermocouples at various positions for temperature monitoring
- Total height of 21mm

## Running the Code

To generate the 2D visualizations:

```bash
cd figure-apparatus-2d
python generate_apparatus_2d.py
```

This will create rendered images in a `renders` subdirectory, including:
- `apparatus_with_glass.png/pdf/svg`: Cross-section view with glass panes
- `apparatus_without_glass.png/pdf/svg`: Cross-section view without glass panes

## Requirements

The script requires the following Python packages:
- numpy
- matplotlib

## Configuration

Key parameters are defined at the top of the `generate_apparatus_2d.py` file and can be modified as needed:

- `TOTAL_HEIGHT`: Total height of the apparatus (21mm)
- `CORK_DIAMETER`: Diameter of cork layers (90mm)
- `CORK_HOLE_DIAMETER`: Diameter of holes in cork (40mm)
- `GLASS_DIAMETER`: Diameter of glass panes (50mm)
- `LAYER_THICKNESS`: Thickness of each layer (1mm)
- `GLASS_THICKNESS`: Thickness of glass panes (2mm)
- `THERMOCOUPLE_THICKNESS`: Thickness of thermocouples (1mm)
- `TOP_CORK_LAYERS`: Number of cork layers at the top (3)
- `BOTTOM_CORK_LAYERS`: Number of cork layers at the bottom (5)

Colors and visual properties can also be customized by modifying the color constants.