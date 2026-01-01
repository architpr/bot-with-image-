import os
import base64
from langchain_core.documents import Document
from src.config import ASSETS_DIR
import streamlit as st

def process_and_index_pdf(pdf_path, vectorstore):
    """
    FAST MODE: Converts PDF -> Images -> Extracts Raw Text (PyMuPDF) -> Vector Store.
    Bypasses Gemini Vision for Speed. 
    Retrieval links text matches to the visual page image.
    """
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    print(f"Processing Visuals (Fast Mode) for: {pdf_path}")
    st.info("Switching to Fast Visual Indexing (Text-Based Linking)...")
    
    # Force usage of PyMuPDF (Fitz)
    try:
        import fitz  # pymupdf
        doc = fitz.open(pdf_path)
    except ImportError:
        st.error("PyMuPDF (fitz) is required but missing.")
        raise RuntimeError("Please install pymupdf: pip install pymupdf")

    documents_to_index = []
    
    progress_bar = st.progress(0, text="Starting fast analysis...")
    total_pages = len(doc)

    for i, page in enumerate(doc):
        page_num = i + 1
        progress_bar.progress((i + 1) / total_pages, text=f"Indexing Page {page_num} of {total_pages}...")
        
        # 1. Save Image Locally (High Res)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image_filename = f"page_{page_num}_{os.path.basename(pdf_path)}.png"
        image_path = os.path.join(ASSETS_DIR, image_filename)
        pix.save(image_path)
        
        # 2. Extract Text instantly
        text_content = page.get_text()
        
        # Fallback if page is strictly image-only (no text layer)
        if not text_content.strip():
            text_content = f"Page {page_num} (Visual Content Only). See image for details."

        # 3. Create Document linked to Image
        doc_obj = Document(
            page_content=text_content, 
            metadata={
                "source": pdf_path, 
                "page": page_num, 
                "image_path": image_path 
            }
        )
        documents_to_index.append(doc_obj)

    st.success(f"Successfully processed {len(documents_to_index)} pages instantly.")

    # Index the DOCUMENTS
    if documents_to_index:
        st.info(f"Indexing {len(documents_to_index)} pages into Knowledge Base...")
        vectorstore.add_documents(documents_to_index)
        st.success("Indexing Complete! You can now ask questions.")
        return len(documents_to_index)
    else:
        st.warning("No content found to index.")
        return 0
