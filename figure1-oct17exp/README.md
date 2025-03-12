# Figure 1: Temperature Profiles of Experimental Apparatus

This directory contains the code and data needed to generate Figure 1 of the paper.

## Description

Figure 1 shows temperature profiles of the experimental apparatus during Trial 2, illustrating thermal response across different surface configurations. The plot tracks four temperature sensors and shows alternating experimental configurations (CCCC - clear bottom, BBBB - black bottom).

## Files

- `plot_trial2.py`: Main script to generate the figure
- `data/trials2.csv`: Raw temperature data from Trial 2
- `data/trial2_annotations.txt`: Configuration annotations for the experiment
- `data/figure1_caption.txt`: Generated caption for the figure

## How to Run

To generate Figure 1, run the following command from within this directory:

```bash
python plot_trial2.py
```

This will:
1. Load and process the experimental temperature data
2. Create the publication-quality plot with all annotations
3. Save the figure as `figure1.png`
4. Save the caption as `data/figure1_caption.txt`