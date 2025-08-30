import numpy as np
from .utils import generate_rainbow_colors, convert_image_to_uint8
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional, Literal
import os
from scipy.ndimage import zoom

def create_multiview(
    image: np.ndarray, 
    colors: Optional[List[Tuple[int, int, int]]] = None, 
    shift: Optional[Tuple[float, float]] = (0.1, 0.1), #shift_y #shift_y
    shift_type: Literal["relative", "absolute"] = "relative", 
    margins: Tuple[float, float] = (0.1, 0.1), 
    fontsize: int = 15, 
    channel_names: Optional[List[str]] = None,
    image_scaling: Optional[float] = 1,
    channels_to_show: Optional[List[int]] = None,
    alpha_value: Optional[int] = 255):
    """
    Create a multiview image from a single multi-channel image.

    Args:
    image (np.ndarray): The input image with multiple channels.
    colors (Optional[List[Tuple[int, int, int]]]): List of RGB tuples for coloring each channel.
    shift (Optional[Tuple[float, float]]): Tuple of shift values with (x_shift, y_shift)
    shift_type (Literal["relative", "absolute"]): Determines if the shift is relative to image size or absolute pixels.
    margins (Tuple[float, float]): Margins to be added around the final image.
    fontsize (int): Font size for channel names.
    channel_names (Optional[List[str]]): Names for each channel to be displayed.

    Returns:
    Image: The resulting multiview image.

    Raises:
    ValueError: If the input image does not have three dimensions.
    FileNotFoundError: If the specified font file is not found.
    AssertionError: If the shift type is not 'relative' or 'absolute'.
    """
    
    image = convert_image_to_uint8(image)

    # Check if the image has three dimensions (height, width, channels)
    if image.ndim != 3:
        raise ValueError("Input image must have three dimensions (height, width, channels)")
    
    if channels_to_show is not None:
        image = image[..., channels_to_show]

    # here code that scales the image hgiven in the formal W H C to the size W*image_scaling H*image_scaling C
    if image_scaling is not None:
        image = zoom(image, (image_scaling, image_scaling, 1), order=0)  # order=3 for cubic interpolation

    # Transpose the image to get channels in the first dimension
    transposed_image = image.transpose(2, 0, 1)
    num_channels, im_height, im_width = transposed_image.shape
    
    # Ensure the shift type is valid
    assert shift_type in ["relative", "absolute"], "Unknown shift type please choose one of 'relative' or 'absolute'."

    # Calculate shifts in pixels if the shift type is relative
    if shift_type == "relative":
        x_shift = int(im_width * shift[0])
        y_shift = int(im_height * shift[1])
        
    else:
        x_shift = int(shift[0])
        y_shift = int(shift[1])
        
    # Set default colors if not provided
    if colors is None:
        if num_channels == 3:
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        else:
            colors = generate_rainbow_colors(num_channels)

    # Path to the font file
    font_path = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found at {font_path}")

    # Load the font for channel names
    font = ImageFont.truetype(font_path, fontsize)
    
    # Calculate the size of the canvas needed to fit all shifted images
    needed_x, needed_y = (num_channels - 1) * x_shift + im_width, (num_channels - 1) * y_shift + im_height
    margin_x, margin_y = margins[0] * needed_x, margins[1] * needed_y
    canvas_size = (int(needed_x + margin_x), int(needed_y + margin_y))

    canvas = Image.new('RGBA', canvas_size, 'white')
    draw = ImageDraw.Draw(canvas)

    # Process each channel
    for n, (channel, color) in enumerate(zip(transposed_image, colors)):
        # Convert single channel to RGB
        rgb_channel = np.stack((channel,) * 3, axis=-1) / 255
        color_array = np.full(rgb_channel.shape, color, dtype=np.uint8)
        colored_channel = Image.fromarray((rgb_channel * color_array).astype(np.uint8)).convert('RGBA')

        # Add alpha channel
        alpha = Image.new('L', colored_channel.size, alpha_value)
        colored_channel.putalpha(alpha)

        # Calculate position for each channel image
        image_position = (int(canvas.size[0] - im_width - n * x_shift - margin_x // 2), int(margin_y // 2 + n * y_shift))

        # Create a temporary image to handle alpha compositing
        temp_image = Image.new('RGBA', canvas.size)
        temp_image.paste(colored_channel, image_position, colored_channel)

        # Alpha composite the temporary image with the canvas
        canvas = Image.alpha_composite(canvas, temp_image)

        # Add channel names if provided
        if channel_names is not None:
            font = ImageFont.load_default()  # Use default font or load a specific one if needed
            text_position = (int(canvas.size[0] - margin_x // 2 - n * x_shift + fontsize // 2), int(margin_y // 2 + im_height + n * y_shift))
            draw.text(text_position, channel_names[n], fill="black", font=font, anchor="lb")

    return canvas
