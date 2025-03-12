# Experimental Data Analysis and Visualization

This repository contains code to generate and analyze data from experiments on thermal radiation transmission through different optical materials. The codebase is organized into three main sections, each corresponding to a figure in the paper.

## Repository Structure

The repository is organized into three main directories, one for each figure, plus a utilities directory:

- **Figure 1** (`/figure1`): Temperature profiles of experimental apparatus during trials
- **Figure 2** (`/figure2`): Temperature vs. Insolation by pane configuration
- **Figure 3** (`/figure3`): Graybody emission and material transmission
- **Utils** (`/utils`): Shared utility modules for data generation

Each directory contains:
- Python scripts to generate the corresponding figure
- Data files needed for analysis
- A README.md with instructions on how to run the code
- Generated figure captions

## How to Run the Code

Each figure can be generated independently by navigating to its directory and running the corresponding Python script:

### Figure 1
```bash
cd figure1
python plot_trial2.py
```

### Figure 2
```bash
cd figure2
python plot_figure2.py
```

### Figure 3
```bash
cd figure3
python combined_plot.py
```

## Required Dependencies

The code requires the following Python packages:
- numpy
- matplotlib
- pandas
- scipy

You can install all dependencies with:
```bash
pip install numpy matplotlib pandas scipy
```

## Figures Description

### Figure 1: Temperature Profiles
Shows temperature profiles of the experimental apparatus during Trial 2, illustrating thermal response across different surface configurations. The plot tracks four temperature sensors and shows alternating experimental configurations.

### Figure 2: Temperature vs. Insolation
Presents the relationship between peak temperature and insolation measurements for different experimental pane configurations. It displays both total insolation and the insolation reaching the bottom for each configuration.

### Figure 3: Graybody Emission
Displays thermal radiation transmission through optical materials from a 65°C graybody. It shows the spectral radiance across wavelengths and illustrates how borosilicate glass and calcium fluoride (CaF₂) transmit different portions of the thermal radiation spectrum.

## Note About Original Files

The original implementation files (plot_trial2.py, plot_figure2.py, combined_plot.py, etc.) are kept in the root directory for reference. The reorganized structure in the figure-specific directories provides a cleaner, more maintainable approach, while preserving all the original functionality.