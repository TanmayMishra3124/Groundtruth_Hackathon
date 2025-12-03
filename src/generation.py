try:
    import torch
    from diffusers import StableDiffusionInpaintPipeline, StableDiffusionImg2ImgPipeline
except ImportError:
    torch = None
    StableDiffusionInpaintPipeline = None
    StableDiffusionImg2ImgPipeline = None

from PIL import Image, ImageOps, ImageDraw
import os

# Check for MPS (Mac) or CUDA
if torch:
    device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device != "cpu" else torch.float32
else:
    device = "cpu"
    dtype = None

MODEL_ID = "runwayml/stable-diffusion-v1-5"
LOCAL_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "stable-diffusion-v1-5")
if os.path.exists(LOCAL_MODEL_PATH):
    MODEL_ID = LOCAL_MODEL_PATH
    print(f"Using local model from: {MODEL_ID}")

class CreativeGenerator:
    def __init__(self):
        self.pipe = None
        self.device = device
        print(f"Initializing Generator on {self.device}...")

    def load_model(self):
        if torch is None:
            print("Warning: torch/diffusers not installed. Using mock generation.")
            return

        if self.pipe is None:
            try:
                # Switching to Text-to-Image for Background Generation as per user request
                from diffusers import StableDiffusionPipeline
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    MODEL_ID,
                    torch_dtype=dtype,
                    use_safetensors=False,
                    safety_checker=None
                ).to(self.device)
                print("Model loaded successfully (Text-to-Image).")
            except Exception as e:
                print(f"Error loading model: {e}")

    def add_shadow(self, product_image, offset=(10, 10), blur_radius=15, shadow_color=(0, 0, 0, 100)):
        """
        Adds a drop shadow to the product image.
        """
        from PIL import ImageFilter
        
        # Create shadow layer
        shadow = Image.new("RGBA", product_image.size, (0, 0, 0, 0))
        
        # Extract alpha to use as shadow shape
        alpha = product_image.split()[-1]
        
        # Create shadow color image
        shadow_layer = Image.new("RGBA", product_image.size, shadow_color)
        shadow_layer.putalpha(alpha)
        
        # Paste shadow with offset
        shadow.paste(shadow_layer, offset, shadow_layer)
        
        # Blur shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        return shadow

    def generate(self, product_image, prompt, negative_prompt="", steps=30, guidance_scale=7.5, seed=None):
        """
        Generates a background using Text-to-Image and composites the product on top.
        """
        if torch is None or self.pipe is None:
            if torch is None:
                self.load_model()
            elif self.pipe is None:
                self.load_model()
                if self.pipe is None and torch:
                     return None

        # Mock generation if no pipe
        if self.pipe is None:
            print(f"Mock Generating for prompt: {prompt[:30]}...")
            import random
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            base_image = Image.new("RGB", product_image.size, color)
            base_image.paste(product_image, (0, 0), product_image)
            return base_image

        generator = torch.Generator(self.device).manual_seed(seed) if seed else None

        try:
            # 1. Generate Background (Text-to-Image)
            
            bg_output = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=512,
                width=512,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                generator=generator
            ).images[0]
            
            bg_output = bg_output.resize(product_image.size, Image.Resampling.LANCZOS)
            
            shadow_layer = self.add_shadow(product_image)
            
            final_comp = Image.alpha_composite(bg_output.convert("RGBA"), shadow_layer)
            final_comp = Image.alpha_composite(final_comp, product_image)
            
            return final_comp.convert("RGB")
            
        except Exception as e:
            print(f"Generation error: {e}")
            return None

def overlay_logo(background_image, logo_path, position="top-right", scale=0.15, padding=20):
    """
    Overlays a logo on the generated image.
    """
    try:
        logo = Image.open(logo_path).convert("RGBA")
        bg_w, bg_h = background_image.size
        
        # Resize logo
        target_w = int(bg_w * scale)
        aspect = logo.height / logo.width
        target_h = int(target_w * aspect)
        logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Calculate position
        if position == "top-right":
            x = bg_w - target_w - padding
            y = padding
        elif position == "top-left":
            x = padding
            y = padding
        elif position == "bottom-right":
            x = bg_w - target_w - padding
            y = bg_h - target_h - padding
        elif position == "bottom-left":
            x = padding
            y = bg_h - target_h - padding
        else:
            x, y = padding, padding
            
        # Paste
        final_img = background_image.copy()
        final_img.paste(logo, (x, y), logo)
        return final_img
    except Exception as e:
        print(f"Logo overlay error: {e}")
        return background_image

if __name__ == "__main__":
    print("Generation module loaded.")
