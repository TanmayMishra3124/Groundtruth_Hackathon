import os
try:
    from groq import Groq
except ImportError:
    Groq = None
import requests
import json

class CaptionGenerator:
    def __init__(self, provider="groq", api_key=None, model="openai/gpt-oss-120b"):
        self.provider = provider
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.model = model
        self.client = None
        
        if provider == "groq":
            if Groq and self.api_key:
                self.client = Groq(api_key=self.api_key)
            else:
                print("Groq provider selected but sdk not installed or key missing.")
        
    def generate_caption(self, product_name, visual_style, brand_tone="professional"):
        """
        Generates ad copy based on product info and visual style using Groq.
        """
        prompt = f"""
        Write a short, catchy social media ad caption for {product_name}.
        The image features the product in a {visual_style} setting.
        Brand tone: {brand_tone}.
        Include 3 relevant hashtags.
        """
        
        if self.provider == "groq" and self.client:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=1,
                    max_completion_tokens=8192,
                    top_p=1,
                    reasoning_effort="medium",
                    stream=True,
                    stop=None
                )
                
                full_response = ""
                for chunk in completion:
                    full_response += chunk.choices[0].delta.content or ""
                return full_response.strip()
            except Exception as e:
                print(f"Groq API error: {e}")
                return f"Experience the best with {product_name}. #Brand #Quality"
        
        else:
            return f"New arrival: {product_name}. #Brand #New"

    def generate_image_prompts(self, product_name, n=4):
        """
        Generates 'n' distinct Stable Diffusion prompts for the product.
        """
        if not self.client:
            # Fallback prompts if no API
            return [
                "minimalist studio background, soft lighting, podium",
                "nature scene, forest floor, sunlight, bokeh",
                "luxury marble countertop, elegant lighting",
                "futuristic neon background, cyber style"
            ]
            
        prompt = f"""
        Generate {n} distinct, creative, and high-quality text-to-image prompts for the BACKGROUND of a product shot for "{product_name}".
        
        CRITICAL INSTRUCTIONS:
        1. Describe ONLY the background setting, lighting, texture, and atmosphere.
        2. DO NOT include the name "{product_name}" or the product type (e.g. bottle, shoe, car) in the prompt.
        3. The background must be EMPTY and clean. NO other objects, NO text, NO labels.
        4. Focus on materials (marble, wood, water), lighting (soft, cinematic, neon), and vibe.
        
        Example Output: "minimalist white marble podium, soft morning light, blurred botanical shadows, high key photography"
        
        Return ONLY the prompts, one per line. No numbering.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=1024,
                top_p=1,
                stream=False
            )
            
            response_text = completion.choices[0].message.content.strip()
            prompts = [line.strip() for line in response_text.split('\n') if line.strip()]
            return prompts[:n]
            
        except Exception as e:
            print(f"Error generating prompts: {e}")
            return [
                f"professional product photography of {product_name}, studio lighting, 4k",
                f"{product_name} on a wooden table, natural sunlight, blurred background",
                f"cinematic shot of {product_name}, dramatic lighting, dark background",
                f"pastel colored background, soft shadows, {product_name} centered"
            ]

if __name__ == "__main__":
    gen = CaptionGenerator(provider="mock")
    print(gen.generate_caption("Running Shoes", "Neon City"))
