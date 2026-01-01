import fitz
import sys

try:
    doc = fitz.open("data/input/sample.pdf")
    print(f"Opened successfully. Pages: {len(doc)}")
    for page in doc:
        print(page.get_text()[:50])
except Exception as e:
    print(f"Error: {e}")
