import numpy as np
import colorsys

def generate_rainbow_colors(num_colors):
    
    # Using HSV (Hue, Saturation, Value) color space to generate rainbow colors and then converting them to RGB
    hues = np.linspace(0, 1, num_colors, endpoint=False)
    hsv_colors = np.column_stack((hues, np.ones_like(hues), np.ones_like(hues)))
    rgb_colors = np.array([colorsys.hsv_to_rgb(*color) for color in hsv_colors])

    rgb_colors = np.uint8(rgb_colors * 255)

    return [tuple(color) for color in rgb_colors]


def convert_image_to_uint8(image: np.ndarray) -> np.ndarray:

    # Check if the image is already in np.uint8 format
    if image.dtype == np.uint8:
        return image

    # Check if the image range is between 0 and 1
    if image.min() >= 0 and image.max() <= 1:
        # Scale the image to 0-255 and convert to np.uint8
        return (image * 255).astype(np.uint8)
    
    if image.min() >= 0 and image.max() <= 255:
        return (image).astype(np.uint8)

    # If the image is not in the expected range, raise an error
    raise ValueError(f"Image values are not in the expected range (0-1 or already in uint8 format). {image.min()} , {image.max()}")
