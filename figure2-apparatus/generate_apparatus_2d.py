#!/usr/bin/env python3
"""
Generate a 2D cross-section visualization of the experimental apparatus using Matplotlib.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import os

# Configuration
# Dimensions in mm
TOTAL_HEIGHT = 21
CORK_DIAMETER = 90
CORK_HOLE_DIAMETER = 40
GLASS_DIAMETER = 50
LAYER_THICKNESS = 1
GLASS_THICKNESS = 2 * LAYER_THICKNESS  # 2mm (2 layers)
THERMOCOUPLE_THICKNESS = 1

# Number of cork layers
TOP_CORK_LAYERS = 3
BOTTOM_CORK_LAYERS = 5

# Colors
CORK_COLOR = '#CD853F'  # SaddleBrown
BLACK_BOTTOM_COLOR = '#1A1A1A'  # Almost black
GLASS_COLOR = '#ADD8E6'  # Light blue
GLASS_ALPHA = 0.6

# Thermocouple colors
RED_TC_COLOR = 'red'  # Top of black bottom
BLUE_TC_COLOR = 'blue'  # Top of bottom pane
GREEN_TC_COLOR = 'green'  # Under bottom pane
PURPLE_TC_COLOR = 'purple'  # Underside of apparatus
BROWN_TC_COLOR = '#8c564b'  # Top pane topside (matches figure3a)

# Figure settings
DPI = 300
FIG_WIDTH = 10
FIG_HEIGHT = 12
MARGIN = 10  # mm

def setup_figure():
    """Set up the matplotlib figure with proper dimensions"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    
    # Set equal aspect ratio
    ax.set_aspect('equal')
    
    # Set limits
    ax.set_xlim(-CORK_DIAMETER/2 - MARGIN, CORK_DIAMETER/2 + MARGIN)
    ax.set_ylim(-MARGIN, TOTAL_HEIGHT + MARGIN)
    
    # Remove axes
    ax.axis('off')
    
    # Set title
    ax.set_title('Apparatus Cross-Section', fontsize=16, pad=20)
    
    return fig, ax

def draw_cork_layer(ax, y_position, is_black_bottom=False, draw_hole=True):
    """Draw a cork layer at the specified height
    
    For layers with holes, we draw two separate rectangles (left and right of hole)
    to avoid drawing a white rectangle that could have borders.
    
    For cork layers with holes, we also add black tips on the inside edge of each side
    that line up exactly with the glass edges.
    
    For the black bottom, which is a full layer without a hole, we draw it as a regular
    cork color layer but with black portions only in the areas where glass would be.
    """
    cork_color = BLACK_BOTTOM_COLOR if is_black_bottom else CORK_COLOR
    
    if not draw_hole and not is_black_bottom:
        # Draw single solid rectangle for fully filled regular cork layers
        cork = patches.Rectangle(
            (-CORK_DIAMETER/2, y_position),
            CORK_DIAMETER, LAYER_THICKNESS,
            facecolor=cork_color,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(cork)
        return [cork]
    elif is_black_bottom and not draw_hole:
        # Special case for black bottom - full cork layer but with black only in middle
        left_width = (CORK_DIAMETER - GLASS_DIAMETER) / 2
        
        # Left side (cork color)
        left_cork = patches.Rectangle(
            (-CORK_DIAMETER/2, y_position),
            left_width, LAYER_THICKNESS,
            facecolor=CORK_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(left_cork)
        
        # Middle section (black color)
        middle_section = patches.Rectangle(
            (-GLASS_DIAMETER/2, y_position),
            GLASS_DIAMETER, LAYER_THICKNESS,
            facecolor=BLACK_BOTTOM_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(middle_section)
        
        # Right side (cork color)
        right_cork = patches.Rectangle(
            (GLASS_DIAMETER/2, y_position),
            left_width, LAYER_THICKNESS,
            facecolor=CORK_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(right_cork)
        
        return [left_cork, middle_section, right_cork]
    else:
        # Calculate dimensions
        left_width = (CORK_DIAMETER - CORK_HOLE_DIAMETER) / 2
        
        # Calculate how far the black tip should extend to line up exactly with glass
        black_tip_width = (GLASS_DIAMETER - CORK_HOLE_DIAMETER) / 2  # Exact alignment with glass edge
        
        # Left side of hole
        left_cork = patches.Rectangle(
            (-CORK_DIAMETER/2, y_position),
            left_width - black_tip_width, LAYER_THICKNESS,  # Reduced for the black tip
            facecolor=cork_color,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(left_cork)
        
        # Black tip on the right edge of the left cork section
        left_black_tip = patches.Rectangle(
            (-CORK_DIAMETER/2 + left_width - black_tip_width, y_position),
            black_tip_width, LAYER_THICKNESS,  # Extends to glass edge
            facecolor=BLACK_BOTTOM_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(left_black_tip)
        
        # Right side of hole
        right_cork = patches.Rectangle(
            (CORK_HOLE_DIAMETER/2 + black_tip_width, y_position),  # Shifted for the black tip
            left_width - black_tip_width, LAYER_THICKNESS,  # Reduced for the black tip
            facecolor=cork_color,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(right_cork)
        
        # Black tip on the left edge of the right cork section
        right_black_tip = patches.Rectangle(
            (CORK_HOLE_DIAMETER/2, y_position),
            black_tip_width, LAYER_THICKNESS,  # Extends to glass edge
            facecolor=BLACK_BOTTOM_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(right_black_tip)
        
        return [left_cork, right_cork, left_black_tip, right_black_tip]

def draw_glass_layer(ax, y_position, pane_number, cork_side):
    """Draw a complete glass layer with cork on specified side
    
    Parameters:
    ----------
    cork_side : str
        'left' - cork on left side, empty on right (Panes 1,3)
        'right' - cork on right side, empty on left (Panes 2,4)
    """
    # Calculate dimensions
    total_side_width = (CORK_DIAMETER - GLASS_DIAMETER) / 2
    
    # Draw glass in the center
    glass = patches.Rectangle(
        (-GLASS_DIAMETER/2, y_position),
        GLASS_DIAMETER, GLASS_THICKNESS,
        facecolor=GLASS_COLOR,
        edgecolor='black',
        alpha=GLASS_ALPHA,
        linewidth=0.5,
        label=f'Pane {pane_number}'
    )
    ax.add_patch(glass)
    
    # Draw two separate 1mm cork layers on specified side
    if cork_side == 'left':
        # First cork layer on left side
        left_cork1 = patches.Rectangle(
            (-CORK_DIAMETER/2, y_position),  # Left edge
            total_side_width, LAYER_THICKNESS,  # Width from edge to glass, 1mm height
            facecolor=CORK_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(left_cork1)
        
        # Second cork layer on left side
        left_cork2 = patches.Rectangle(
            (-CORK_DIAMETER/2, y_position + LAYER_THICKNESS),  # Left edge, 1mm up
            total_side_width, LAYER_THICKNESS,  # Width from edge to glass, 1mm height
            facecolor=CORK_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(left_cork2)
    else:  # cork_side == 'right'
        # First cork layer on right side
        right_cork1 = patches.Rectangle(
            (GLASS_DIAMETER/2, y_position),  # Right edge of glass
            total_side_width, LAYER_THICKNESS,  # Width to right edge, 1mm height
            facecolor=CORK_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(right_cork1)
        
        # Second cork layer on right side
        right_cork2 = patches.Rectangle(
            (GLASS_DIAMETER/2, y_position + LAYER_THICKNESS),  # Right edge of glass, 1mm up
            total_side_width, LAYER_THICKNESS,  # Width to right edge, 1mm height
            facecolor=CORK_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(right_cork2)
    
    return glass

def draw_thermocouple(ax, x_position, y_position, color, size=THERMOCOUPLE_THICKNESS, label=None):
    """Draw a thermocouple at the specified position"""
    tc = patches.Circle(
        (x_position, y_position),
        radius=size/2,
        facecolor=color,
        edgecolor='black',
        linewidth=0.5,
        label=label
    )
    ax.add_patch(tc)
    
    return tc

def draw_apparatus(ax, with_glasses=True):
    """Draw the complete apparatus"""
    # Start from bottom
    y_position = 0
    
    # Draw bottom cork layers (no hole in bottom cork layers)
    for i in range(BOTTOM_CORK_LAYERS):
        draw_cork_layer(ax, y_position, draw_hole=False)
        y_position += LAYER_THICKNESS
    
    # Draw Black Bottom with same pattern as cork layers with holes
    black_bottom_objects = draw_cork_layer(ax, y_position, is_black_bottom=True, draw_hole=False)
    black_bottom_y = y_position
    y_position += LAYER_THICKNESS
    
    # Draw glass panes with cork separators
    glass_panes = []
    glass_positions = []
    
    for i in range(4):  # 4 glass panes
        # For first pane, draw a cork separator
        if i == 0:
            # Cork separator with holes
            draw_cork_layer(ax, y_position, draw_hole=True)
            y_position += LAYER_THICKNESS
        
        # Glass pane with cork on alternating sides
        if with_glasses:
            # Pane 1 and 3: cork on left side, empty on right
            if i == 0 or i == 2:
                glass = draw_glass_layer(ax, y_position, i+1, cork_side='left')
            # Pane 2 and 4: cork on right side, empty on left
            else:
                glass = draw_glass_layer(ax, y_position, i+1, cork_side='right')
                
            glass_panes.append(glass)
            glass_positions.append(y_position)
        y_position += GLASS_THICKNESS
        
        # Cork separator between glass panes (only one layer)
        draw_cork_layer(ax, y_position, draw_hole=True)
        y_position += LAYER_THICKNESS
    
    # Draw top cork layers (subtract 1 since we already drew one cork layer after the last glass pane)
    for i in range(TOP_CORK_LAYERS - 1):
        draw_cork_layer(ax, y_position, draw_hole=True)
        y_position += LAYER_THICKNESS
    
    # Draw thermocouples if glass panes are present
    if with_glasses:
        # Red thermocouple - top of black bottom (centered)
        red_tc = draw_thermocouple(
            ax,
            0,  # Centered
            black_bottom_y + LAYER_THICKNESS,
            RED_TC_COLOR,
            label="Red TC"
        )
        
        # Blue thermocouple - top of bottom pane
        blue_tc = draw_thermocouple(
            ax,
            GLASS_DIAMETER/2 - THERMOCOUPLE_THICKNESS,
            glass_positions[0] + GLASS_THICKNESS,
            BLUE_TC_COLOR,
            label="Blue TC"
        )
        
        # Green thermocouple - under bottom pane
        green_tc = draw_thermocouple(
            ax,
            0,
            glass_positions[0],
            GREEN_TC_COLOR,
            label="Green TC"
        )
        
        # Purple thermocouple - underside of apparatus (centered)
        purple_tc = draw_thermocouple(
            ax,
            0,  # Centered
            0,
            PURPLE_TC_COLOR,
            label="Purple TC"
        )
        
        # Brown thermocouple - top of top pane (4th glass pane)
        brown_tc = draw_thermocouple(
            ax,
            -GLASS_DIAMETER/2 + THERMOCOUPLE_THICKNESS,  # Opposite of blue TC
            glass_positions[3] + GLASS_THICKNESS,
            BROWN_TC_COLOR,
            label="Brown TC"
        )
    
    # Add dimension lines and labels
    # Overall height
    ax.arrow(-CORK_DIAMETER/2 - 5, 0, 0, TOTAL_HEIGHT, 
             head_width=1, head_length=1, fc='black', ec='black', length_includes_head=True)
    ax.arrow(-CORK_DIAMETER/2 - 5, TOTAL_HEIGHT, 0, -TOTAL_HEIGHT, 
             head_width=1, head_length=1, fc='black', ec='black', length_includes_head=True)
    ax.text(-CORK_DIAMETER/2 - 8, TOTAL_HEIGHT/2, f'{TOTAL_HEIGHT} mm', 
            rotation=90, ha='center', va='center')
    
    # Cork diameter
    ax.arrow(-CORK_DIAMETER/2, -6, CORK_DIAMETER, 0, 
             head_width=1, head_length=1, fc='black', ec='black', length_includes_head=True)
    ax.arrow(CORK_DIAMETER/2, -6, -CORK_DIAMETER, 0, 
             head_width=1, head_length=1, fc='black', ec='black', length_includes_head=True)
    ax.text(0, -8, f'{CORK_DIAMETER} mm', ha='center', va='center')
    
    # Glass diameter - moved below the apparatus
    if with_glasses and glass_positions:
        y_glass_label = -2  # Position below the apparatus
        ax.arrow(-GLASS_DIAMETER/2, y_glass_label, GLASS_DIAMETER, 0, 
                 head_width=1, head_length=1, fc='black', ec='black', length_includes_head=True)
        ax.arrow(GLASS_DIAMETER/2, y_glass_label, -GLASS_DIAMETER, 0, 
                 head_width=1, head_length=1, fc='black', ec='black', length_includes_head=True)
        ax.text(0, y_glass_label - 2, f'{GLASS_DIAMETER} mm', ha='center', va='center')
    
    # Add text labels - all on the right side
    ax.text(CORK_DIAMETER/2 + 5, black_bottom_y + LAYER_THICKNESS/2, 
            'Black Bottom', ha='left', va='center')
    
    if with_glasses:
        for i, pos in enumerate(glass_positions):
            ax.text(CORK_DIAMETER/2 + 5, pos + GLASS_THICKNESS/2, 
                    f'Pane {i+1}', ha='left', va='center')
    
    # Add legend for thermocouples
    if with_glasses:
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor=RED_TC_COLOR, markersize=10, label='TC Black Bottom'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=BLUE_TC_COLOR, markersize=10, label='TC Bottom Pane Topside'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=GREEN_TC_COLOR, markersize=10, label='TC Bottom Pane Underside'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=PURPLE_TC_COLOR, markersize=10, label='TC Apparatus Underside'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor=BROWN_TC_COLOR, markersize=10, label='TC Top Pane Topside')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1.2))

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
    # Draw with glass panes
    fig, ax = setup_figure()
    draw_apparatus(ax, with_glasses=True)
    save_figure(fig, "apparatus_with_glass")
    plt.close(fig)
    
    # Draw without glass panes
    fig, ax = setup_figure()
    draw_apparatus(ax, with_glasses=False)
    save_figure(fig, "apparatus_without_glass")
    plt.close(fig)
    
    print("Done! Figures have been saved to the 'renders' directory.")

if __name__ == "__main__":
    main()