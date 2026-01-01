import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extractor import PDFExtractor

print("Initializing Extractor")
extractor = PDFExtractor()
print("Extracting...")
try:
    data = extractor.extract("data/input/sample.pdf")
    print(f"Success. Found {len(data)} items.")
except Exception as e:
    import traceback
    traceback.print_exc()
