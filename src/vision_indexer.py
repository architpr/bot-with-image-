import os
import base64
from pdf2image import convert_from_path
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.config import ASSETS_DIR, GOOGLE_API_KEY
from src.llm_utils import invoke_with_retry

# Initialize Vision Model (Gemini 3 Flash Preview)
# Using Gemini 3 as a substitute for the decommissioned Groq Vision model
vision_llm = ChatGoogleGenerativeAI(
    model="models/gemini-3-flash-preview", 
    google_api_key=GOOGLE_API_KEY,
    temperature=0
)

def encode_image(image_path):
    """Helper to convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_pdf_with_vision(pdf_path, output_dir=ASSETS_DIR):
    """
    1. Converts PDF pages to images.
    2. Uses Vision LLM (Gemini 3) to describe them.
    3. Returns Documents with image_path in metadata.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Processing Visuals for: {pdf_path}")
    
    try:
        # Convert PDF to images
        # Poppler must be in PATH. If on Windows and not in PATH, this might fail.
        # Users often need to download poppler binaries and add 'bin' to PATH.
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        print("Ensure Poppler is installed and added to PATH.")
        return []

    documents = []

    for i, img in enumerate(images):
        # Save image locally
        # Use a consistent naming convention
        image_filename = f"visual_summary_page_{i+1}_{os.path.basename(pdf_path)}.png"
        image_path = os.path.join(output_dir, image_filename)
        img.save(image_path, "PNG")

        print(f"Describing Page {i+1}...")
        
        # Prepare prompt for the Vision Model
        base64_image = encode_image(image_path)
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Analyze this page image. Describe any diagrams, figures, charts, or tables in detail. If there is a Figure label (e.g., 'Figure 1'), include it explicitly. Summarize the main text visible. This description will be used for retrieval."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        )
        
        try:
            # Invoke with retry logic
            response = invoke_with_retry(vision_llm, [message])
            description = response.content
        except Exception as e:
            print(f"Error describing page {i+1}: {e}")
            description = f"Visual description unavailable for page {i+1}."

        print(f"Generated Description for Page {i+1}: {description[:50]}...")

        # Create Document with Link to Image
        # Note: 'image_path' metadata key is critical for the UI to display it
        # The chain.py also expects 'image_path' list. 
        # We'll stick to the requested single 'image_path' key but the chain.py logic handles lists/single.
        
        doc = Document(
            page_content=description,  # This is what the retriever searches against
            metadata={
                "source": pdf_path, 
                "page": i+1, 
                "image_path": image_path  # The UI will pick this up
            }
        )
        documents.append(doc)

    return documents
