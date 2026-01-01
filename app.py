import streamlit as st
import os
import shutil
from src.visual_processor import process_and_index_pdf
from src.vectorstore import get_retriever
from src.chain import get_chain
from src.config import INPUT_DIR, ASSETS_DIR, CHROMA_DB_DIR
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import ast

st.set_page_config(page_title="Deep Multimodal RAG (Visual Summaries)", layout="wide")

st.title("Deep Multimodal RAG (Visual)")
st.markdown("Visual Summarization with Gemini 3 Flash + pdf2image.")

# Sidebar for processing
with st.sidebar:
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        file_path = os.path.join(INPUT_DIR, uploaded_file.name)
        
        # Save file
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Saved {uploaded_file.name}")
            
            # Processing logic
            
        # Processing Button (Always visible if file is uploaded)
        st.divider()
        st.subheader("Document Processing")
        
        status_container = st.empty()
        
        if st.button("Process Document (Visual)"):
            status_container.info("Starting Processing (Fast Mode)...")
            with st.spinner("Extracting Visuals & Text (Fast Processor)..."):
                try:
                    # Clear existing DB to prevent stale non-visual chunks
                    if os.path.exists(CHROMA_DB_DIR):
                        try:
                            shutil.rmtree(CHROMA_DB_DIR)
                            status_container.warning("Cleared old Knowledge Base.")
                        except OSError as e:
                            status_container.warning(f"File Lock: Could not clear old DB (Used by other process). Appending new data instead...")
                            # we do NOT stop here, we try to proceed.
                    
                    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                    vectorstore = Chroma(
                        collection_name="rag_collection",
                        embedding_function=embeddings,
                        persist_directory=CHROMA_DB_DIR
                    )
                    
                    # Process and Index directly
                    count = process_and_index_pdf(file_path, vectorstore)
                    if count > 0:
                        status_container.success(f"Ingestion Complete! Indexed {count} Visual Summaries.")
                        st.balloons()
                    else:
                        status_container.warning("Processed PDF but no documents were indexed.")

                except RuntimeError as re:
                        status_container.error(f"System Error: {re}")
                        st.error("Please ensure Poppler is installed or PyMuPDF fell back correctly.")
                except Exception as e:
                    status_container.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "images" in message:
            for img in message["images"]:
                if os.path.exists(img):
                    st.image(img, caption="Retrieved Reference", width=400)

if prompt := st.chat_input("Ask a question about the document"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing text and images..."):
            try:
                # Initialize Chain
                chain = get_chain()
                
                # Retrieve context just for UI display
                retriever = get_retriever()
                docs = retriever.invoke(prompt)

                relevant_images = []

                # Debugging Section
                with st.expander("Debug: Multi-Vector Metadata"):
                    st.write(f"Retrieved {len(docs)} text chunks")
                    if len(docs) == 0:
                         st.warning("No documents retrieved. Check if Ingestion succeeded.")
                         # Check collection count
                         try:
                             from src.config import CHROMA_DB_DIR
                             from langchain_chroma import Chroma
                             from langchain_huggingface import HuggingFaceEmbeddings
                             embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                             vs = Chroma(collection_name="rag_collection", embedding_function=embeddings, persist_directory=CHROMA_DB_DIR)
                             st.write(f"Total Docs in DB: {vs._collection.count()}")
                         except:
                             pass

                    for i, d in enumerate(docs):
                        st.write(f"Doc {i} Metadata: {d.metadata}")
                        # visual_processor saves 'image_path' as string, not list
                        path = d.metadata.get("image_path")
                        if path:
                            relevant_images.append(path)
                            with st.container():
                                st.write(f"**Linked Image**: {path}")
                                if os.path.exists(path):
                                    st.image(path, caption=f"Reference for Doc {i}", width=400)
                                else:
                                    st.error(f"Image Missing: {path}")

                # Invoke Chain
                response_text = chain.invoke(prompt)
                st.markdown(response_text)
                
                # Save history

                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "images": relevant_images
                })
            except Exception as e:
                import traceback
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    st.error("⚠️ **Google AI Rate Limit Hit (Free Tier)**")
                    st.warning("The system is sending too many requests too quickly for the free API plan.")
                    st.warning("Please wait 30-60 seconds and try again.")
                else:
                    st.error(f"Error during generation: {e}")
                    st.code(traceback.format_exc())
