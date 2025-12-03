import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import AutoCreativeEngine
from src.input_handler import get_inputs

def main():
    print("=== Auto-Creative Engine ===")
    
    # Check if arguments provided
    if len(sys.argv) == 3:
        logo_path = sys.argv[1]
        product_path = sys.argv[2]
    else:
        logo_path, product_path = get_inputs()
        
    if logo_path and product_path:
        engine = AutoCreativeEngine()
        engine.run(logo_path, product_path)
    else:
        print("Aborted.")

if __name__ == "__main__":
    main()
