import streamlit as st
import os
import sys
from PIL import Image

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import AutoCreativeEngine

st.set_page_config(page_title="Auto-Creative Engine", layout="wide")

def save_uploaded_file(uploaded_file, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    path = os.path.join(dest_folder, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def generate_creatives(logo_file, product_file, product_name, api_key):
    with st.spinner("Processing... This may take a minute."):
        try:
            inputs_dir = os.path.join(os.getcwd(), "inputs")
            logo_path = save_uploaded_file(logo_file, inputs_dir)
            product_path = save_uploaded_file(product_file, inputs_dir)

            os.environ["GROQ_API_KEY"] = api_key

            engine = AutoCreativeEngine()
            
            zip_path, results = engine.run(logo_path, product_path, product_name)
            
            st.success("Generation Complete!")
            
            st.subheader("2. Generated Results")
            
            cols = st.columns(2)
            for i, res in enumerate(results):
                img = res['image']
                caption_text = res['caption']
                
                with cols[i % 2]:
                    st.image(img, use_container_width=True)
                    st.caption(f"**Caption**: {caption_text}")
                    st.divider()

            with open(zip_path, "rb") as fp:
                btn = st.download_button(
                    label="📥 Download All (ZIP)",
                    data=fp,
                    file_name=os.path.basename(zip_path),
                    mime="application/zip"
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")
            import traceback
            st.code(traceback.format_exc())

def main():
    st.title("🎨 Auto-Creative Engine")
    st.markdown("Upload your brand logo and product image to generate AI creatives.")

    # Hardcoded API Key
    # TODO: Replace with your actual Groq API Key or set via environment variable
    api_key = os.environ.get("GROQ_API_KEY", "YOUR_API_KEY_HERE")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Upload Inputs")
        logo_file = st.file_uploader("Brand Logo (PNG)", type=['png', 'jpg', 'jpeg'])
        product_file = st.file_uploader("Product Image", type=['png', 'jpg', 'jpeg'])
        product_name = st.text_input("Product Name", value="My Product")

    if logo_file:
        with col1:
            st.image(logo_file, caption="Logo Preview", width=100)
    
    if product_file:
        with col1:
            st.image(product_file, caption="Product Preview", width=200)

    if logo_file and product_file:
        if st.button("🚀 Generate Creatives", type="primary"):
             generate_creatives(logo_file, product_file, product_name, api_key)

if __name__ == "__main__":
    main()
