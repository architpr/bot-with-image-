from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import os

def create_pdf(path):
    # check dir
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    
    # Text
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Deep Multimodal RAG Test Document")
    c.drawString(100, 730, "This document contains a table and an image to test extraction.")
    
    # Table (drawn manually as text for simplicity)
    c.drawString(100, 700, "Table 1: Item Inventory")
    c.drawString(100, 685, "ID   | Name       | Qty")
    c.drawString(100, 670, "-------------------------")
    c.drawString(100, 655, "001  | Widget A   | 50")
    c.drawString(100, 640, "002  | Widget B   | 150")
    c.drawString(100, 625, "003  | Gadget X   | 20")
    
    # Image
    # Create a dummy image
    img_path = "temp_chart.png"
    img = Image.new('RGB', (200, 200), color = (0, 150, 255)) # Blue square
    img.save(img_path)
    
    c.drawImage(img_path, 100, 400, width=200, height=200)
    c.drawString(100, 380, "Figure 1: A Blue Box Visual.")
    
    c.save()
    if os.path.exists(img_path):
        os.remove(img_path)
    print(f"Created {path}")

if __name__ == "__main__":
    create_pdf("d:/ML project/GraphRAG expert/data/input/sample.pdf")
