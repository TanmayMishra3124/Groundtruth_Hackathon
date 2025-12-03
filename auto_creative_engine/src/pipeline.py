import os
import shutil
import zipfile
from datetime import datetime
from PIL import Image

from .input_handler import get_inputs, validate_image
from .preprocessing import resize_image, remove_background, create_composition
from .preprocessing import resize_image, remove_background, create_composition
# from .prompt_manager import load_base_prompt, load_variations, construct_prompt # Removed
from .generation import CreativeGenerator, overlay_logo
from .generation import CreativeGenerator, overlay_logo
from .captioning import CaptionGenerator

class AutoCreativeEngine:
    def __init__(self):
        self.generator = CreativeGenerator()
        self.captioner = CaptionGenerator(provider="groq") # Default to Groq
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.output_dir = os.path.join(self.base_dir, "final_output")
        self.generated_dir = os.path.join(self.base_dir, "generated_images")
        self.raw_dir = os.path.join(self.generated_dir, "raw")
        self.final_dir = os.path.join(self.generated_dir, "final")
        self.captions_dir = os.path.join(self.base_dir, "captions")
        
        os.makedirs(self.output_dir, exist_ok=True)
        # Directories are now created in run() to be temporary
        # os.makedirs(self.raw_dir, exist_ok=True)
        # os.makedirs(self.final_dir, exist_ok=True)
        # os.makedirs(self.captions_dir, exist_ok=True)

    def run(self, logo_path, product_path, product_name="Product"):
        print("Starting Auto-Creative Engine...")
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)
        os.makedirs(self.captions_dir, exist_ok=True)
        
        print("Preprocessing images...")
        product_img = Image.open(product_path).convert("RGBA")
        logo_img = Image.open(logo_path).convert("RGBA")
        
        try:
            product_img = remove_background(product_img)
        except:
            print("Background removal skipped (module not working).")
            
        product_img = create_composition(product_img, background_size=(1024, 1024), product_scale=0.8)
        
        preprocessing_dir = os.path.join(self.base_dir, "preprocessing")
        os.makedirs(preprocessing_dir, exist_ok=True)
        preprocessed_path = os.path.join(preprocessing_dir, "processed_input.png")
        product_img.save(preprocessed_path)
        print(f"Saved preprocessed image to {preprocessed_path}")
        
        print(f"Generating dynamic prompts for '{product_name}'...")
        
        try:
            variations = self.captioner.generate_image_prompts(product_name, n=4)
            print(f"Generated {len(variations)} prompts.")
        except Exception as e:
            print(f"Failed to generate prompts: {e}")
            variations = ["clean studio background", "outdoor nature scene", "luxury setting", "minimalist pastel"]
        
        generated_files = []
        caption_files = []
        
        print(f"Generating {len(variations)} variations...")
        results = []
        
        for i, var_prompt in enumerate(variations):
            full_prompt = f"{var_prompt}, empty scene, background texture only, no objects"
            print(f"Variation {i+1}: {full_prompt}")
            
            negative_prompt = "text, watermark, label, writing, signature, logo, brand, typography, bad quality, blurry, distorted, other products, bottles, boxes"
            gen_img = self.generator.generate(product_img, full_prompt, negative_prompt=negative_prompt)
            if gen_img:
                raw_filename = f"raw_{i+1:03d}.png"
                raw_path = os.path.join(self.raw_dir, raw_filename)
                gen_img.save(raw_path)

                final_img = overlay_logo(gen_img, logo_path)
                
                filename = f"creative_{i+1:03d}.png"
                save_path = os.path.join(self.final_dir, filename)
                final_img.save(save_path)
                generated_files.append(save_path)
                
                caption = self.captioner.generate_caption(product_name, var_prompt)
                cap_filename = f"caption_{i+1:03d}.txt"
                cap_path = os.path.join(self.captions_dir, cap_filename)
                with open(cap_path, "w") as f:
                    f.write(caption)
                caption_files.append(cap_path)
                
                results.append({
                    "image": final_img,
                    "caption": caption
                })
                
        print("Packaging results...")
        zip_name = f"auto_creative_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(self.output_dir, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for f in generated_files:
                zf.write(f, os.path.basename(f))
            for f in caption_files:
                zf.write(f, os.path.basename(f))
                
        print(f"Done! Results saved to {zip_path}")
        
        print("Cleaning up intermediate files...")
        try:
            shutil.rmtree(self.generated_dir)
            shutil.rmtree(self.captions_dir)
            preprocessing_dir = os.path.join(self.base_dir, "preprocessing")
            if os.path.exists(preprocessing_dir):
                shutil.rmtree(preprocessing_dir)
        except Exception as e:
            print(f"Cleanup warning: {e}")

        return zip_path, results

if __name__ == "__main__":
    # CLI Entry point
    l, p = get_inputs()
    if l and p:
        engine = AutoCreativeEngine()
        engine.run(l, p)
