import os
from PIL import Image
try:
    from rembg import remove
except ImportError:
    remove = None

def resize_image(image_path, target_size=(1024, 1024)):
    """
    Resizes an image to the target size, maintaining aspect ratio and padding if necessary,
    or just resizing to cover. For Stable Diffusion, exact dimensions are often preferred.
    Here we'll resize to contain within target_size and then paste on a centered background
    or just resize to fill. Let's go with resize to fill for simplicity or standard resize.
    
    Args:
        image_path (str): Path to the input image.
        target_size (tuple): Desired (width, height).
        
    Returns:
        PIL.Image: Resized image.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Create a new image with the target size and paste the resized image onto it
        new_img = Image.new("RGBA", target_size, (255, 255, 255, 0))
        
        # Calculate position to center the image
        left = (target_size[0] - img.width) // 2
        top = (target_size[1] - img.height) // 2
        
        new_img.paste(img, (left, top), img)
        return new_img
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def remove_background(image):
    """
    Removes the background from a PIL Image using rembg.
    Also attempts to fill 'holes' inside the product (e.g. white labels removed by mistake)
    by restoring the original pixels.
    
    Args:
        image (PIL.Image): Input image.
        
    Returns:
        PIL.Image: Image with background removed.
    """
    if remove is None:
        print("Warning: rembg not installed. Skipping background removal.")
        return image
        
    try:
        no_bg = remove(image)
        
        if no_bg.size != image.size:
            return no_bg
            
        alpha = no_bg.split()[-1]
        
        mask = Image.new("L", alpha.size, 0)
        mask.paste(alpha, (0, 0))
        mask = mask.point(lambda p: 255 if p > 10 else 0)
        
        from PIL import ImageDraw
        
        work_mask = alpha.copy()
        ImageDraw.floodfill(work_mask, (0, 0), 128, thresh=10)
        ImageDraw.floodfill(work_mask, (0, work_mask.height-1), 128, thresh=10)
        ImageDraw.floodfill(work_mask, (work_mask.width-1, 0), 128, thresh=10)
        ImageDraw.floodfill(work_mask, (work_mask.width-1, work_mask.height-1), 128, thresh=10)
        
        final_img = no_bg.copy()
        original_rgba = image.convert("RGBA")
        
        hole_mask = work_mask.point(lambda p: 255 if p == 0 else 0)
        final_img.paste(original_rgba, (0, 0), hole_mask)
        
        return final_img
        
    except Exception as e:
        print(f"Error removing background: {e}")
        return image

def create_composition(product_image, background_size=(1024, 1024), product_scale=0.8, product_position="center"):
    """
    Creates a composition with the product image placed on a blank canvas.
    This is a placeholder for more complex composition logic.
    
    Args:
        product_image (PIL.Image): The product image (transparent background).
        background_size (tuple): Size of the canvas.
        product_scale (float): Scale of product relative to canvas.
        product_position (str): 'center', 'bottom', etc.
        
    Returns:
        PIL.Image: Composed image (product on transparent layer).
    """
    canvas = Image.new("RGBA", background_size, (0, 0, 0, 0))
    
    # Resize product to fit scale
    target_w = int(background_size[0] * product_scale)
    target_h = int(background_size[1] * product_scale)
    
    product_image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Position
    if product_position == "center":
        x = (background_size[0] - product_image.width) // 2
        y = (background_size[1] - product_image.height) // 2
    elif product_position == "bottom":
        x = (background_size[0] - product_image.width) // 2
        y = background_size[1] - product_image.height - 50 # 50px padding
    else:
        x, y = 0, 0
        
    canvas.paste(product_image, (x, y), product_image)
    return canvas

if __name__ == "__main__":
    # Test stub
    print("Preprocessing module loaded.")
