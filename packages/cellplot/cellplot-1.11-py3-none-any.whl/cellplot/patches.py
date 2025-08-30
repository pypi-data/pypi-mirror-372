import numpy as np
import matplotlib.pyplot as plt
from typing import List, Union, Tuple
import cv2

COLOR_DICT = {1: (1,0,0), 2: (0,1,0), 3:(1,1,0), 4:(0, 1, 1)}


def gridPlot(
    images, 
    overlay=None, 
    titles=None, 
    grid_size=(10, 10), 
    layout="auto", 
    channels_to_show: Union[None, List[int]] = None, 
    plot_size: Tuple = (10, 10), 
    hspace=0.4, 
    vspace=0.4,
    alpha=0.2,
    show_plot=True,
    vmin=0,
    vmax=1):
    
    if titles is not None and len(titles) != len(images):
        raise ValueError("Length of titles list must match number of images!")
    
    if titles is None: 
        titles = [""]*len(images)
    
    images = images[:grid_size[0]*grid_size[1]]
    overlay = overlay[:grid_size[0]*grid_size[1]] if overlay is not None else [None for _ in range(len(images))]

    # Check if input is a numpy array
    if isinstance(images, np.ndarray):
        # Reshape 3D array to 4D with 1 channel if needed
        if len(images.shape) == 3:
            images = images[..., np.newaxis]
        n, w, h, c = images.shape
    elif isinstance(images, (list, tuple)):
        # Convert to list of numpy arrays
        images = [np.asarray(im) for im in images]
        n = len(images)
        c = max([im.shape[-1] for im in images]) if any([im.ndim == 3 for im in images]) else 1    
    else:
        raise TypeError("Invalid input type. Expected 4D/3D numpy array or list/tuple of 2D/3D arrays.")
    
    # Determine the channels to show
    if channels_to_show is None:
        channels_to_show = [0, 1, 2] if c > 3 else np.arange(c)
    elif not all([isinstance(ch, int) and 0 <= ch < c for ch in channels_to_show]):
        raise ValueError(f"Invalid channel index in channels_to_show. Must be integers between 0 and {c-1}.")
    elif len(channels_to_show) not in [1, 3]:
        raise ValueError(f"To show {len(channels_to_show)} number of channels is not implemented, either provide None, 1 or 3 channels.")

    nrows, ncols = grid_size
    
    # Determine the optimal grid size if n is less than nrows * ncols
    if layout == "auto":
        if n < nrows * ncols:
            nrows = int(np.ceil(np.sqrt(n)))
            ncols = nrows

    fig, axes = plt.subplots(nrows, ncols, figsize=plot_size)
    
    # Flatten the axes array and hide unused subplots
    axes_flat = axes.ravel()
    for ax in axes_flat[n:]:
        ax.axis('off')
    
    for ax, im, over, title in zip(axes_flat[:n], images, overlay, titles):
        if im.ndim == 3:  # Multi-channel image
            ax.imshow(im[..., channels_to_show], vmin=vmin, vmax=vmax)
        else:  # Single channel image
            ax.imshow(im, cmap='gray', vmin=vmin, vmax=vmax)
        if over is not None:
            ax.imshow(over, alpha=alpha, cmap='gray', vmin=vmin, vmax=vmax)
        
        ax.axis('off')
        
        if title is not None:
            ax.set_title(title, fontsize=10)
    
    plt.subplots_adjust(hspace=hspace, wspace=vspace)
    
    if show_plot:
        plt.show()
        
    else:
        return fig, axes

# Example usage:
# gridPlot(np.random.rand(20, 64, 64, 4), channels_to_show=[0, 2, 3])  # 4D array, custom channels
# gridPlot(np.random.rand(20, 64, 64))  # 3D array
# gridPlot([np.random.rand(64, 64, 4) for _ in range(20)], channels_to_show=[0, 1, 2])  # List of 3D arrays


def draw_boxes_on_patch(patch, boxes, labels, scores=None, threshold=0.5, thickness=1):
    """
    Draws bounding boxes on the given image patch using cv2.

    Parameters:
    - patch: The image patch.
    - boxes: List of bounding boxes. Each box is a tuple (min_y, min_x, max_y, max_x).
    - labels: List of labels corresponding to each box.
    - scores: List of confidence scores corresponding to each box.
    - threshold: Minimum confidence score for a box to be drawn.
    - thickness: Width of the box lines.

    Returns:
    - The image patch with drawn bounding boxes.
    """
    if isinstance(scores, type(None)):
        scores = np.ones(len(labels))
        
    patch = np.ascontiguousarray(patch)
    
    for box, label, score in zip(boxes, labels, scores):
        if score >= threshold:
            min_x, min_y, max_x, max_y = min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3])
            cv2.rectangle(patch, (min_x, min_y), (max_x, max_y), COLOR_DICT[label], thickness)

    return patch
