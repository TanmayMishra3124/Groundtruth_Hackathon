import os
from PIL import Image

SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg']
MIN_RESOLUTION = (512, 512)
MAX_FILE_SIZE_MB = 10

def validate_image(file_path):
    """
    Validates the input image file.
    
    Args:
        file_path (str): Path to the image file.
        
    Returns:
        bool: True if valid, False otherwise.
        str: Error message if invalid.
    """
    if not os.path.exists(file_path):
        return False, "File does not exist."
        
    # Check extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        return False, f"Unsupported format: {ext}. Supported: {SUPPORTED_FORMATS}"
        
    # Check file size
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size too large: {size_mb:.2f}MB. Max: {MAX_FILE_SIZE_MB}MB"
        
    # Check resolution
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            if width < MIN_RESOLUTION[0] or height < MIN_RESOLUTION[1]:
                return False, f"Resolution too low: {width}x{height}. Min: {MIN_RESOLUTION[0]}x{MIN_RESOLUTION[1]}"
    except Exception as e:
        return False, f"Invalid image file: {e}"
        
    return True, "Valid"

def get_inputs():
    """
    Simple CLI to get input paths from user.
    In a real app, this would be a UI or API endpoint.
    """
    print("--- Auto-Creative Engine Input ---")
    logo_path = input("Enter path to Brand Logo (PNG preferred): ").strip()
    product_path = input("Enter path to Product Image: ").strip()
    
    valid_logo, msg_logo = validate_image(logo_path)
    if not valid_logo:
        print(f"Logo Error: {msg_logo}")
        return None, None
        
    valid_prod, msg_prod = validate_image(product_path)
    if not valid_prod:
        print(f"Product Error: {msg_prod}")
        return None, None
        
    return logo_path, product_path

if __name__ == "__main__":
    l, p = get_inputs()
    if l and p:
        print(f"Inputs accepted:\nLogo: {l}\nProduct: {p}")
