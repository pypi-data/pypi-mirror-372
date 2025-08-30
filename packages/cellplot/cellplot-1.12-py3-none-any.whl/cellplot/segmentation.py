import numpy as np    
import matplotlib.pyplot as plt
import matplotlib
import cv2
import matplotlib.colors as mcolors
from skimage.segmentation import find_boundaries
from scipy.ndimage import binary_dilation

def create_transparent_colormap(base_cmap):
    base = plt.cm.get_cmap(base_cmap)
    base_colors = base(np.arange(base.N))
    new_colors = np.zeros((base.N, 4))
    new_colors[:, :3] = base_colors[:, :3]
    new_colors[0, 3] = 0  # Fully transparent
    new_colors[1:, 3] = 1  # Fully opaque
    transparent_cmap = mcolors.ListedColormap(new_colors, name='transparent_{}'.format(base_cmap))
    return transparent_cmap

def rand_col_seg(seg) -> np.ndarray:
    
    vals = np.unique(seg)
    colors = np.random.uniform(0.1, 1, (vals.max()+1, 3))
    colors[0] = [0, 0, 0]

    return colors[seg]

def contoure_seg(masks, ret_rgb=True, rgb_color=[1, 0, 0], dilate=False):
    # Find object boundaries
    boundaries = find_boundaries(masks, mode='outer')
    
    # Optionally apply dilation to thicken the contour lines
    if dilate:
        boundaries = binary_dilation(boundaries, iterations=dilate if isinstance(dilate, int) else 1)
    
    if ret_rgb:
        contour_image = np.zeros((*boundaries.shape, 3), dtype=np.float32)
        contour_image[boundaries] = rgb_color  # e.g., red
    else:
        contour_image = boundaries.astype(np.float32)

    return contour_image
        
def plot_image_and_segmentation(
    
    image: np.ndarray, 
    segmentation_mask: np.ndarray, 
    figsize=(10, 5), 
    axis="off", 
    overlap=True, 
    alpha=0.5, 
    random_color_segmentation=False, 
    cmap="gray",
    contours=False,
    dilate=False) -> matplotlib.figure.Figure:
      
    assert not(random_color_segmentation and contours), "random_color_segmentation and contours can not be set at the same time to True"
    
    if random_color_segmentation and not contours:
        segmentation_mask = rand_col_seg(segmentation_mask)
        
    elif not random_color_segmentation and contours:
        segmentation_mask = contoure_seg(segmentation_mask, dilate=dilate)
        
    if overlap:
        
        image = image / image.max()
        
        fig, axs = plt.subplots(1, 1, figsize=figsize)
        axs.imshow(image, cmap=cmap)
        axs.imshow(segmentation_mask, alpha=alpha, cmap=create_transparent_colormap("gray"))
        axs.axis(axis)
        return fig
        
    else:
        fig, axs = plt.subplots(1, 2, figsize=figsize)
        for ax, im in zip(axs.ravel(), [image, segmentation_mask]):
            ax.imshow(im)
            ax.axis(axis)
        
        return fig


    