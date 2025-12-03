# H-003 | The AI Creative Studio

🚀 **The Auto-Creative Engine**
**Tagline**: An automated creative engine that transforms product images into diverse, high-quality ad creatives with AI-generated copy in seconds.

---

## 1. The Problem (Real World Scenario)
**Context**: In the fast-paced world of digital marketing, brands need to constantly test new ad creatives to combat ad fatigue. A single campaign might require dozens of variations.

**The Pain Point**: Manually designing these variations is slow, expensive, and unscalable. Designers spend hours on repetitive tasks like background replacement and resizing, creating a bottleneck in the marketing workflow.

**My Solution**: An automated "Auto-Creative Engine" that takes a brand's assets (Logo + Product) and uses Generative AI to instantly produce multiple high-quality ad variations with matching, on-brand copy.

## 2. Expected End Result
**For the User**:
1.  Uploads a **Brand Logo** and **Product Image**.
2.  Enters a **Groq API Key**.
3.  Clicks **Generate**.
4.  Receives a gallery of **AI-generated ad creatives** (product placed in diverse scenes) with **AI-written captions**.
5.  Downloads a **ZIP file** containing all assets ready for deployment.

## 3. Technical Approach
The system follows a linear pipeline:
1.  **Input Handling**: Streamlit UI accepts user uploads and API keys.
2.  **Preprocessing**: 
    *   **Background Removal**: Uses `rembg` (U2Net) to isolate the product.
    *   **Composition**: Intelligently scales and positions the product on a transparent canvas to ensure optimal placement for inpainting.
3.  **Image Generation**: 
    *   Uses **Stable Diffusion v1.5** (Inpainting Pipeline) to generate context-aware backgrounds around the product based on predefined style prompts (Minimalist, Nature, Luxury, Futuristic).
    *   **Logo Overlay**: Automatically superimposes the brand logo on the generated images.
4.  **Text Generation**: 
    *   Uses **Groq API (Llama 3)** to generate catchy, style-specific ad captions and hashtags.
5.  **Output**: Packages all images and text files into a structured ZIP archive.

## 4. Tech Stack
*   **Language**: Python 3.9
*   **Interface**: Streamlit
*   **Generative AI (Image)**: Stable Diffusion v1.5 (`diffusers`, `torch`)
*   **Generative AI (Text)**: Groq API (`groq` python sdk)
*   **Image Processing**: Pillow, RemBG, OnnxRuntime
*   **Environment**: Virtual Environment (`venv`)

## 5. Challenges & Learnings
*   **Python Version Compatibility**: The initial environment (Python 3.14) lacked support for critical ML libraries like `pyarrow` (Streamlit dependency) and `rembg`. **Solution**: Downgraded to Python 3.9 using a custom virtual environment.
*   **Model Loading Issues**: The downloaded Stable Diffusion weights were in `.bin` format, but the pipeline defaulted to `safetensors`, causing load failures. **Solution**: Explicitly configured the pipeline to disable `use_safetensors`.
*   **Image Quality & Composition**: Early generations had the product zoomed in too far, leaving no room for background generation. **Solution**: Implemented a composition step to scale the product to 80% of the canvas size before inpainting.
*   **Dependency Management**: `rembg` failed silently due to missing `onnxruntime`. **Solution**: Added robust error handling and installed the missing dependency.
