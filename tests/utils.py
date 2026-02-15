
import os
import io
from PIL import Image
import piexif

def create_dummy_image(filename, format='JPEG', size=(100, 100), exif_data=None):
    """
    Creates a dummy image with optional EXIF data.
    """
    image = Image.new('RGB', size, color='red')
    
    exif_bytes = None
    if exif_data:
        exif_bytes = piexif.dump(exif_data)
    
    if format == 'JPEG':
        if exif_bytes:
            image.save(filename, format=format, exif=exif_bytes)
        else:
            image.save(filename, format=format)
    else:
        # PNG and others might verify differently, but Pillow handles basic saving
        image.save(filename, format=format)
    
    return filename

def create_heavy_dummy_image(filename, target_size_mb):
    """
    Creates a dummy JPEG image approximately of the target size in MB.
    """
    # Create a large image
    # 1 MB is roughly 1024*1024 pixels with 3 channels (RGB) uncompressed, 
    # but JPEG compression reduces this. We'll use a larger dimension.
    # A 5000x5000 image is 25MP.
    
    # Simpler approach: Create a file with random bytes but valid header? 
    # No, Pillow needs to open it.
    # Let's write valid JPEG data then append junk?
    # Better: Create a large canvas.
    
    side = int((target_size_mb * 1024 * 1024 / 3) ** 0.5) * 2 # Crude approximation
    image = Image.new('RGB', (side, side), color='blue')
    image.save(filename, "JPEG", quality=100) # Max quality to maximize size
    return filename

def get_exif_data(filename):
    """Returns EXIF data as a dict."""
    try:
        img = Image.open(filename)
        if 'exif' in img.info:
            return piexif.load(img.info['exif'])
        return None
    except Exception:
        return None
