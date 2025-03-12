#!/usr/bin/env python3
"""
Generate a top-down visualization of the experimental apparatus using Matplotlib.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import os

# Import configuration from cross-section visualization
from generate_apparatus_2d import (
    CORK_DIAMETER, CORK_HOLE_DIAMETER, GLASS_DIAMETER, 
    LAYER_THICKNESS, CORK_COLOR, BLACK_BOTTOM_COLOR, GLASS_COLOR, GLASS_ALPHA,
    RED_TC_COLOR, BLUE_TC_COLOR, GREEN_TC_COLOR, PURPLE_TC_COLOR, BROWN_TC_COLOR,
    THERMOCOUPLE_THICKNESS, DPI, MARGIN
)

# Figure settings for top-down view
FIG_WIDTH = 6  # Even smaller
FIG_HEIGHT = 6  # Square aspect for circular view but smaller overall

def setup_figure():
    """Set up the matplotlib figure with proper dimensions"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    
    # Set equal aspect ratio
    ax.set_aspect('equal')
    
    # Set limits with same scale as cross-section view
    max_dim = max(CORK_DIAMETER, CORK_DIAMETER) / 2 + MARGIN
    ax.set_xlim(-max_dim, max_dim)
    ax.set_ylim(-max_dim, max_dim)
    
    # Remove axes
    ax.axis('off')
    
    # Set title
    ax.set_title('Apparatus Top-Down View', fontsize=16, pad=20)
    
    return fig, ax

def draw_top_down_view(ax, with_glass=True):
    """Draw the top-down view of the apparatus"""
    # Draw outer cork circle
    outer_cork = patches.Circle(
        (0, 0),
        radius=CORK_DIAMETER/2,
        facecolor=CORK_COLOR,
        edgecolor='black',
        linewidth=0.5
    )
    ax.add_patch(outer_cork)

    # gdaw 5cm diameter black hole
    black_hole = patches.Circle(
        (0, 0),
        radius=GLASS_DIAMETER/2,
        facecolor=BLACK_BOTTOM_COLOR,
        edgecolor='black',
        linewidth=0.5
    )
    ax.add_patch(black_hole)

    # Draw 4cm inner hole glass-colored
    inner_hole = patches.Circle(
        (0, 0),
        radius=CORK_HOLE_DIAMETER/2,
        facecolor=GLASS_COLOR,
        edgecolor='black',
        alpha=0.7 if with_glass else 0,
        linewidth=0.5
    )
    ax.add_patch(inner_hole)
    
    # # Draw glass-colored interior visible through the hole
    # # Opacity depends on whether we're looking through glass
    # interior_alpha = 0.7 if with_glass else 0.9
    # interior = patches.Circle(
    #     (0, 0),
    #     radius=CORK_HOLE_DIAMETER/2,  # Fill the entire hole with no gap
    #     facecolor=GLASS_COLOR,
    #     alpha=interior_alpha,
    #     edgecolor=None
    # )
    # ax.add_patch(interior)
    
    # # Add black inner ring (just the outer edge painted black)
    # # Calculate the thickness of the black ring
    # black_ring_thickness = 5  # Width of the black painted edge in mm
    
    # # Create black ring as an annular ring (donut shape)
    # black_outer = patches.Circle(
    #     (0, 0),
    #     radius=GLASS_DIAMETER/2,
    #     facecolor=BLACK_BOTTOM_COLOR,
    #     alpha=0.9,
    #     edgecolor=None,
    #     zorder=5
    # )
    # ax.add_patch(black_outer)
    
    # # Create inner circle to punch out the center (making a ring)
    # black_inner_hole = patches.Circle(
    #     (0, 0),
    #     radius=GLASS_DIAMETER/2,
    #     facecolor=GLASS_COLOR,  # Match the glass color for the inner area
    #     alpha=0.7 if with_glass else 0.9,
    #     edgecolor=None,
    #     zorder=6  # Higher zorder to be drawn on top
    # )
    # ax.add_patch(black_inner_hole)
    
    # Draw thermocouples as colored dots
    # Increase zorder to ensure thermocouples stand out at the very top
    tc_zorder = 20
    
    # Red thermocouple - centered (top of black bottom)
    red_tc = patches.Circle(
        (0, 0),
        radius=THERMOCOUPLE_THICKNESS * 1.2,  # Make slightly larger
        facecolor=RED_TC_COLOR,
        edgecolor='black',
        linewidth=0.8,
        zorder=tc_zorder,
        label="Red TC"
    )
    ax.add_patch(red_tc)
    
    # Position the side TCs at the edge of the black inner circle
    # Calculate positions for side thermocouples
    # Position should be at the edge of the black inner circle (GLASS_DIAMETER/2)
    side_position = GLASS_DIAMETER/2
    
    # Blue thermocouple - top of bottom pane (on the side)
    # Position it at the edge of the black inner circle
    blue_x = side_position
    blue_y = 0
    blue_tc = patches.Circle(
        (blue_x, blue_y),
        radius=THERMOCOUPLE_THICKNESS * 1.2,  # Make slightly larger
        facecolor=BLUE_TC_COLOR,
        edgecolor='black',
        linewidth=0.8,
        zorder=tc_zorder,
        label="Blue TC"
    )
    ax.add_patch(blue_tc)
    
    # Green thermocouple - under bottom pane (on the side)
    # Position it inside the cork layer on the opposite side
    green_tc = patches.Circle(
        (blue_y, blue_x),
        radius=THERMOCOUPLE_THICKNESS * 1.2,  # Make slightly larger
        facecolor=GREEN_TC_COLOR,
        edgecolor='black',
        linewidth=0.8,
        zorder=tc_zorder,
        label="Green TC"
    )
    ax.add_patch(green_tc)
    
    # Purple thermocouple - centered (underside of apparatus)
    # Visually differentiate from red by making slightly smaller
    purple_tc = patches.Circle(
        (0, 0),
        radius=THERMOCOUPLE_THICKNESS*0.8,  # Slightly smaller than red but still visible
        facecolor=PURPLE_TC_COLOR,
        edgecolor='black',
        linewidth=0.8,
        zorder=tc_zorder - 1,  # Just below red but still above other elements
        label="Purple TC"
    )
    ax.add_patch(purple_tc)
    
    # Brown thermocouple - top of top pane (opposite to blue TC)
    brown_tc = patches.Circle(
        (-blue_x, blue_y),  # Opposite side from blue TC
        radius=THERMOCOUPLE_THICKNESS * 1.2,
        facecolor=BROWN_TC_COLOR,
        edgecolor='black',
        linewidth=0.8,
        zorder=tc_zorder,
        label="Brown TC"
    )
    ax.add_patch(brown_tc)
    
    # Add dimension lines and labels with higher zorder to stand out
    dim_zorder = 15
    
    # Cork diameter - horizontal
    ax.arrow(-CORK_DIAMETER/2, -CORK_DIAMETER/2 - 5, CORK_DIAMETER, 0, 
             head_width=1, head_length=1, fc='black', ec='black', 
             linewidth=0.8, zorder=dim_zorder, length_includes_head=True)
    ax.arrow(CORK_DIAMETER/2, -CORK_DIAMETER/2 - 5, -CORK_DIAMETER, 0, 
             head_width=1, head_length=1, fc='black', ec='black', 
             linewidth=0.8, zorder=dim_zorder, length_includes_head=True)
    ax.text(0, -CORK_DIAMETER/2 - 8, f'{CORK_DIAMETER} mm', 
            ha='center', va='center', zorder=dim_zorder)
    
    # Cork diameter - vertical
    ax.arrow(-CORK_DIAMETER/2 - 5, -CORK_DIAMETER/2, 0, CORK_DIAMETER, 
             head_width=1, head_length=1, fc='black', ec='black', 
             linewidth=0.8, zorder=dim_zorder, length_includes_head=True)
    ax.arrow(-CORK_DIAMETER/2 - 5, CORK_DIAMETER/2, 0, -CORK_DIAMETER, 
             head_width=1, head_length=1, fc='black', ec='black', 
             linewidth=0.8, zorder=dim_zorder, length_includes_head=True)
    ax.text(-CORK_DIAMETER/2 - 8, 0, f'{CORK_DIAMETER} mm', 
            rotation=90, ha='center', va='center', zorder=dim_zorder)
    
    # Glass diameter (50mm) - at the bottom similar to lateral view
    # Make sure it's more visible by positioning it correctly
    y_glass_label = -25 - 2
    
    # Draw 50mm dimension line with slightly thicker arrows
    ax.arrow(-GLASS_DIAMETER/2, y_glass_label, GLASS_DIAMETER, 0, 
             head_width=1.5, head_length=2, fc='black', ec='black', 
             linewidth=1.0, zorder=dim_zorder, length_includes_head=True)
    ax.arrow(GLASS_DIAMETER/2, y_glass_label, -GLASS_DIAMETER, 0, 
             head_width=1.5, head_length=2, fc='black', ec='black', 
             linewidth=1.0, zorder=dim_zorder, length_includes_head=True)
    
    # Add label without changing the font weight
    ax.text(0, y_glass_label - 3, f'{GLASS_DIAMETER} mm', 
            ha='center', va='center', zorder=dim_zorder)
    
    # Add legend for thermocouples with bolder formatting
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=RED_TC_COLOR, 
               markersize=10, markeredgecolor='black', markeredgewidth=0.5, 
               label='TC Black Bottom'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=BLUE_TC_COLOR, 
               markersize=10, markeredgecolor='black', markeredgewidth=0.5, 
               label='TC Bottom Pane Topside'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=GREEN_TC_COLOR, 
               markersize=10, markeredgecolor='black', markeredgewidth=0.5, 
               label='TC Bottom Pane Underside'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=BROWN_TC_COLOR, 
               markersize=10, markeredgecolor='black', markeredgewidth=0.5, 
               label='TC Top Pane Topside'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=PURPLE_TC_COLOR, 
               markersize=10, markeredgecolor='black', markeredgewidth=0.5, 
               label='TC Apparatus Underside (not visible)')
    ]
    # Position legend below title (centered at top)
    legend = ax.legend(handles=legend_elements, loc='upper right')
    # Don't change font weight

def save_figure(fig, filename):
    """Save the figure in multiple formats"""

    # put in 'renders' of script directory
    output_dir = os.path.join(os.path.dirname(__file__), 'renders')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as PNG
    png_path = os.path.join(output_dir, f"{filename}.png")
    fig.savefig(png_path, dpi=DPI, bbox_inches='tight')
    

def main():
    """Main function to draw and save the apparatus visualization"""
    # Draw with glass (partial opacity for interior)
    fig, ax = setup_figure()
    draw_top_down_view(ax, with_glass=True)
    save_figure(fig, "top_down_with_glass")
    plt.close(fig)
    
    # Draw without glass (higher opacity for interior)
    fig, ax = setup_figure()
    draw_top_down_view(ax, with_glass=False)
    save_figure(fig, "top_down_without_glass")
    plt.close(fig)
    
    print("Done! Top-down view figures have been saved to the 'renders' directory.")

if __name__ == "__main__":
    main()