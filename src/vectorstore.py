from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config import CHROMA_DB_DIR
import shutil
import os

def get_retriever(extracted_data=None, documents=None, collection_name="rag_collection", reset=False):
    """
    Initializes or loads the vector store with HuggingFace embeddings.
    Accepts:
    - extracted_data: List of dicts (Old Extractor)
    - documents: List of LangChain Documents (New Vision Indexer)
    """
    # Use local embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if reset and os.path.exists(CHROMA_DB_DIR):
        shutil.rmtree(CHROMA_DB_DIR)

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

    docs_to_add = []

    # Handle direct Documents (Vision Indexer)
    if documents:
        docs_to_add.extend(documents)
        print(f"Queueing {len(documents)} Documents for ingestion.")

    # Handle extracted_data dicts (Legacy/Fallback)
    if extracted_data:
        documents = []
        for item in extracted_data:
            # Determine content to vectorise
            # For Text: use 'content'
            # For Table/Image: use 'summary'
            
            page_content = item.get("summary") if item.get("summary") else item.get("content")
            
            if not page_content:
                continue

            metadata = item.get("metadata", {})
            metadata["type"] = item.get("type")
            if item.get("image_path"):
                # Serialize list to string for ChromaDB compatibility
                metadata["image_path"] = str(item.get("image_path"))
            
            # Store raw content in metadata
            metadata["raw_content"] = item.get("content")[:5000]

            doc = Document(
                page_content=page_content,
                metadata=metadata
            )
            docs_to_add.append(doc)

    if docs_to_add:
        vectorstore.add_documents(docs_to_add)
        print(f"Added {len(docs_to_add)} documents to vector store.")

    return vectorstore.as_retriever(search_kwargs={"k": 2})
