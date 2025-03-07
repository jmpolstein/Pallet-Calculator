import math
import streamlit as st
import matplotlib.pyplot as plt
import re
from mpl_toolkits.mplot3d import Axes3D

def calculate_max_boxes(pallet_length, pallet_width, pallet_height, overhang, max_stack_height, box_dims):
    # Initialize variables to track the optimal configuration
    max_total = 0
    best_config = {}
    
    # Calculate effective pallet dimensions with overhang
    effective_length = pallet_length + 2 * overhang
    effective_width = pallet_width + 2 * overhang
    
    # Try each dimension as the height
    for i, h in enumerate(box_dims):
        # Get the other two dimensions for the base
        a = box_dims[(i + 1) % 3]
        b = box_dims[(i + 2) % 3]
        
        # Try both alignments of the base dimensions
        alignments = [
            (a, b),  # a along length, b along width
            (b, a)   # b along length, a along width
        ]
        
        for base_a, base_b in alignments:
            # Calculate boxes that fit in each direction
            boxes_length = math.floor(effective_length / base_a)
            boxes_width = math.floor(effective_width / base_b)
            
            # Calculate available height for stacking (accounting for pallet height)
            available_height = max_stack_height - pallet_height
            layers = math.floor(available_height / h)
            
            # Calculate total boxes for this configuration
            total = boxes_length * boxes_width * layers
            
            # Update best configuration if this is better
            if total > max_total:
                max_total = total
                best_config = {
                    'total_boxes': total,
                    'orientation': f'height={h}, base={base_a}x{base_b}',
                    'boxes_along_length': boxes_length,
                    'boxes_along_width': boxes_width,
                    'layers': layers
                }
    
    return best_config

def visualize_arrangement(pallet_length, pallet_width, overhang, result):
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Draw pallet
    pallet = plt.Rectangle((0, 0), pallet_length, pallet_width, 
                          fill=False, edgecolor='k', lw=2, label='Pallet')
    ax.add_patch(pallet)
    
    # Extract box dimensions from the orientation
    orientation = result['orientation']
    match = re.search(r'base=(\d+\.?\d*)x(\d+\.?\d*)', orientation)
    if match:
        box_length_arranged = float(match.group(1))
        box_width_arranged = float(match.group(2))
    else:
        return fig  # Return empty figure if we can't extract dimensions
    
    # Calculate total footprint
    total_length = box_length_arranged * result['boxes_along_length']
    total_width = box_width_arranged * result['boxes_along_width']
    
    # Center the arrangement on the pallet
    start_x = (pallet_length - total_length) / 2
    start_y = (pallet_width - total_width) / 2
    
    # Adjust if using overhang
    start_x = max(start_x, -overhang)
    start_y = max(start_y, -overhang)
    
    # Draw each box
    for i in range(result['boxes_along_length']):
        for j in range(result['boxes_along_width']):
            x = start_x + i * box_length_arranged
            y = start_y + j * box_width_arranged
            box = plt.Rectangle((x, y), box_length_arranged, box_width_arranged,
                              fill=True, edgecolor='blue', facecolor='lightblue', 
                              alpha=0.7)
            ax.add_patch(box)
    
    # Set aspect and limits
    ax.set_aspect('equal')
    ax.set_xlim(-overhang - 1, pallet_length + overhang + 1)
    ax.set_ylim(-overhang - 1, pallet_width + overhang + 1)
    
    # Add title and annotation
    boxes_per_layer = result['boxes_along_length'] * result['boxes_along_width']
    ax.set_title('Optimal Box Arrangement on Pallet (One Layer)')
    ax.text(pallet_length/2, -overhang - 0.5, 
            f"Boxes per layer: {boxes_per_layer}, Total boxes: {result['total_boxes']}\n"
            f"Configuration: {result['orientation']}", 
            horizontalalignment='center', verticalalignment='top')
    
    # Add grid lines and labels
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xlabel('Length (inches)')
    ax.set_ylabel('Width (inches)')
    
    # Show pallet edges more clearly
    plt.plot([0, 0], [0, pallet_width], 'k-', lw=2)
    plt.plot([0, pallet_length], [0, 0], 'k-', lw=2)
    plt.plot([pallet_length, pallet_length], [0, pallet_width], 'k-', lw=2)
    plt.plot([0, pallet_length], [pallet_width, pallet_width], 'k-', lw=2)
    
    # Show overhang boundary with dashed lines if overhang > 0
    if overhang > 0:
        overhang_rect = plt.Rectangle((-overhang, -overhang), 
                                     pallet_length + 2*overhang, 
                                     pallet_width + 2*overhang,
                                     fill=False, edgecolor='red', 
                                     linestyle='--', label='Overhang limit')
        ax.add_patch(overhang_rect)
        ax.legend()
    
    plt.tight_layout()
    return fig

def visualize_3d_pallet(pallet_length, pallet_width, pallet_height,
                       box_length, box_width, box_height,
                       overhang, boxes_along_length, boxes_along_width, layers):
    # Initialize a new 3D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Calculate total footprint of the boxes
    total_length = boxes_along_length * box_length
    total_width = boxes_along_width * box_width
    
    # Determine starting positions to center boxes on the pallet
    # Use the same centering logic as the 2D visualization for consistency
    start_x = (pallet_length - total_length) / 2
    start_y = (pallet_width - total_width) / 2
    
    # Adjust if using overhang
    start_x = max(start_x, -overhang)
    start_y = max(start_y, -overhang)
    
    # Draw the pallet as a wireframe
    # Bottom face of the pallet (z = 0)
    ax.plot([0, pallet_length, pallet_length, 0, 0], 
            [0, 0, pallet_width, pallet_width, 0], 
            [0, 0, 0, 0, 0], color='black', linewidth=2)
    
    # Top face of the pallet (z = pallet_height)
    ax.plot([0, pallet_length, pallet_length, 0, 0], 
            [0, 0, pallet_width, pallet_width, 0], 
            [pallet_height, pallet_height, pallet_height, pallet_height, pallet_height], 
            color='black', linewidth=2)
    
    # Vertical edges of the pallet
    for x in [0, pallet_length]:
        for y in [0, pallet_width]:
            ax.plot([x, x], [y, y], [0, pallet_height], color='black', linewidth=2)
    
    # Draw each layer of boxes
    for layer in range(layers):
        for i in range(boxes_along_length):
            for j in range(boxes_along_width):
                # Calculate box position
                x_left = start_x + i * box_length
                y_left = start_y + j * box_width
                z_bottom = pallet_height + layer * box_height  # Stack above pallet
                
                # Draw bottom face of the box
                ax.plot([x_left, x_left + box_length, x_left + box_length, x_left, x_left],
                        [y_left, y_left, y_left + box_width, y_left + box_width, y_left],
                        [z_bottom, z_bottom, z_bottom, z_bottom, z_bottom], 
                        color='blue', alpha=0.7)
                
                # Draw top face of the box
                ax.plot([x_left, x_left + box_length, x_left + box_length, x_left, x_left],
                        [y_left, y_left, y_left + box_width, y_left + box_width, y_left],
                        [z_bottom + box_height, z_bottom + box_height, z_bottom + box_height, 
                         z_bottom + box_height, z_bottom + box_height], 
                        color='blue', alpha=0.7)
                
                # Draw vertical edges of the box
                for dx in [0, box_length]:
                    for dy in [0, box_width]:
                        ax.plot([x_left + dx, x_left + dx], 
                                [y_left + dy, y_left + dy], 
                                [z_bottom, z_bottom + box_height], 
                                color='blue', alpha=0.7)
    
    # Configure the plot
    ax.set_xlabel("Length (x, inches)")
    ax.set_ylabel("Width (y, inches)")
    ax.set_zlabel("Height (z, inches)")
    ax.set_xlim([-overhang, pallet_length + overhang])
    ax.set_ylim([-overhang, pallet_width + overhang])
    ax.set_zlim([0, pallet_height + layers * box_height + 5])  # Extra space above
    ax.set_title(f"3D Visualization of Pallet with {boxes_along_length}x{boxes_along_width}x{layers} Boxes")
    
    plt.tight_layout()
    return fig

def main():
    st.set_page_config(page_title="Box Stacking Optimizer", layout="wide")
    
    st.title("Box Stacking Optimizer")
    st.write("This application helps you find the optimal arrangement of boxes on a pallet.")
    
    # Create a two-column layout for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Pallet Dimensions (inches)")
        pallet_length = st.number_input("Length", min_value=0.1, value=48.0, step=0.1, format="%.1f")
        pallet_width = st.number_input("Width", min_value=0.1, value=40.0, step=0.1, format="%.1f")
        pallet_height = st.number_input("Height", min_value=0.1, value=5.0, step=0.1, format="%.1f")
    
    with col2:
        st.header("Box Dimensions (inches)")
        box_length = st.number_input("Box Length", min_value=0.1, value=10.0, step=0.1, format="%.1f")
        box_width = st.number_input("Box Width", min_value=0.1, value=8.0, step=0.1, format="%.1f")
        box_height = st.number_input("Box Height", min_value=0.1, value=6.0, step=0.1, format="%.1f")
    
    # Additional parameters in a single column
    st.header("Additional Parameters (inches)")
    overhang = st.number_input("Allowed Overhang per Side (length and width)", 
                               min_value=0.0, value=0.0, step=0.1, format="%.1f")
    max_stack_height = st.number_input("Maximum Available Height for Stacking", 
                                      min_value=pallet_height + 0.1, value=60.0, step=0.1, format="%.1f")
    
    # Calculate button
    if st.button("Calculate Optimal Arrangement", type="primary"):
        with st.spinner("Calculating optimal arrangement..."):
            box_dims = [box_length, box_width, box_height]
            
            result = calculate_max_boxes(
                pallet_length, pallet_width, pallet_height, 
                overhang, max_stack_height, box_dims
            )
            
            # Calculate pallet utilization
            # 1. Calculate box volume
            box_volume = box_length * box_width * box_height
            
            # 2. Define effective dimensions with overhang
            effective_length = pallet_length + 2 * overhang
            effective_width = pallet_width + 2 * overhang
            
            # 3. Calculate available height for stacking
            available_height = max_stack_height - pallet_height
            
            # 4. Get total number of boxes
            total_boxes = result['total_boxes']
            
            # 5. Compute available and utilized volumes
            available_volume = effective_length * effective_width * available_height
            utilized_volume = total_boxes * box_volume
            
            # 6. Calculate utilization percentage
            if available_height > 0 and effective_length > 0 and effective_width > 0:
                utilization_percentage = (utilized_volume / available_volume) * 100
            else:
                utilization_percentage = 0
            
            # Display results in an expandable section
            with st.expander("Optimization Results", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Boxes", result['total_boxes'])
                    st.metric("Boxes per Layer", result['boxes_along_length'] * result['boxes_along_width'])
                
                with col2:
                    st.metric("Layers", result['layers'])
                    st.metric("Pallet Utilization (%)", f"{utilization_percentage:.2f}")
                
                with col3:
                    st.write("**Orientation:**", result['orientation'])
                    st.write("**Boxes along Length:**", result['boxes_along_length'])
                    st.write("**Boxes along Width:**", result['boxes_along_width'])
                
                # Additional utilization details
                st.write("---")
                st.write("**Utilization Details:**")
                details_col1, details_col2 = st.columns(2)
                
                with details_col1:
                    st.write(f"• Box Volume: {box_volume:.2f} cubic inches")
                    st.write(f"• Total Box Volume: {utilized_volume:.2f} cubic inches")
                
                with details_col2:
                    st.write(f"• Available Volume: {available_volume:.2f} cubic inches")
                    st.write(f"• Effective Dimensions: {effective_length:.1f}\" × {effective_width:.1f}\" × {available_height:.1f}\"")
            
            # Extract box dimensions for visualization
            orientation = result['orientation']
            match = re.search(r'height=(\d+\.?\d*), base=(\d+\.?\d*)x(\d+\.?\d*)', orientation)
            
            if match:
                box_h = float(match.group(1))
                box_l = float(match.group(2))
                box_w = float(match.group(3))
                
                # Create visualizations
                st.header("Visualizations")
                viz_col1, viz_col2 = st.columns(2)
                
                with viz_col1:
                    st.subheader("2D Top-Down View")
                    fig_2d = visualize_arrangement(pallet_length, pallet_width, overhang, result)
                    st.pyplot(fig_2d)
                
                with viz_col2:
                    st.subheader("3D Visualization")
                    fig_3d = visualize_3d_pallet(
                        pallet_length, pallet_width, pallet_height,
                        box_l, box_w, box_h, overhang,
                        result['boxes_along_length'], 
                        result['boxes_along_width'], 
                        result['layers']
                    )
                    st.pyplot(fig_3d)
            else:
                st.error("Could not extract box dimensions for visualization.")
                st.subheader("2D Top-Down View")
                fig_2d = visualize_arrangement(pallet_length, pallet_width, overhang, result)
                st.pyplot(fig_2d)

if __name__ == "__main__":
    main() 