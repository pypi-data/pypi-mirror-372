import tifffile
import pathlib
from PIL import Image
import matplotlib.pyplot as plt

class DimensionError(Exception):
    pass

def show_file(file_path):
    
    file = pathlib.Path(file_path)
    
    if file.suffix.lower() in [".jpg", ".png", ".eps", ".svg"]:
        image = Image.open(file)
        
    elif file.suffix.lower() in [".tif", ".tiff"]:
        image = tifffile.imread(file)
        
    else:
        raise ValueError(f"{file.suffix} not implemented filetype!")
        
    if image.ndim != 2 and image.ndim != 3:
        raise DimensionError(f"Image of shape {image.shape} are not implemented to be shown")
    
    if image.ndim == 3 and (image.shape[-1] not in [3, 1]):
        raise DimensionError(f"Channel number {image.shape[-1]} not implemented to be shown")
        
    plt.imshow(image)
    plt.show()
    
    