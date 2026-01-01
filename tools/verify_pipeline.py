import sys
import os
import traceback

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.extractor import PDFExtractor
    from src.vectorstore import get_retriever
    from src.graph import app as graph_app
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_pipeline():
    pdf_path = "data/input/sample.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print("1. Testing Extraction...")
    try:
        extractor = PDFExtractor()
        data = extractor.extract(pdf_path)
        
        print(f"Extracted {len(data)} items.")
        for item in data:
            print(f" - Found {item['type']}")
            if item['type'] == 'Image':
                print(f"   Image Path: {item.get('image_path')}")
                print(f"   Summary: {item.get('summary')}")
    except Exception:
        traceback.print_exc()
        return

    print("\n2. Testing Vector Store Ingestion...")
    try:
        get_retriever(extracted_data=data, reset=True)
    except Exception:
        traceback.print_exc()
        return
    
    print("\n3. Testing Agent Query (Table)...")
    try:
        state = {"question": "How many Widget B do we have?", "retry_count": 0}
        result = graph_app.invoke(state)
        print(f"Q: How many Widget B do we have?\nA: {result['answer']}")

        print("\n4. Testing Agent Query (Image)...")
        state = {"question": "What is shown in Figure 1?", "retry_count": 0}
        result = graph_app.invoke(state)
        print(f"Q: What is shown in Figure 1?\nA: {result['answer']}")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
