import os
import sys

# Add root dir to path
sys.path.append(os.getcwd())

from pdf2image import convert_from_path, pdfinfo_from_path
from src.config import INPUT_DIR, ASSETS_DIR

def diagnose():
    print("--- DIAGNOSTIC START ---")
    
    # 1. Check Poppler
    try:
        from pdf2image.exceptions import PDFInfoNotInstalledError
        print("Checking Poppler...")
        # Try to execute a simple command
        # We need a dummy PDF.
        dummy_pdf = "dummy.pdf"
        with open(dummy_pdf, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources << >>\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000117 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n223\n%%EOF")
        
        try:
            info = pdfinfo_from_path(dummy_pdf)
            print("SUCCESS: Poppler is installed and working.")
            print(f"Poppler Info: {info}")
        except PDFInfoNotInstalledError:
            print("FAIL: Poppler is NOT installed or not in PATH.")
            print("CRITICAL: Visual processing requires Poppler.")
        except Exception as e:
             print(f"FAIL: Poppler check error: {e}")
        
        if os.path.exists(dummy_pdf):
            os.remove(dummy_pdf)
            
    except ImportError:
        print("FAIL: pdf2image not installed.")

    print("--- DIAGNOSTIC END ---")

if __name__ == "__main__":
    diagnose()
