from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from src.config import GOOGLE_API_KEY
from src.vectorstore import get_retriever
from src.llm_utils import invoke_with_retry
import base64
import os
import ast

def multimodal_prompt_builder(inputs):
    """
    Constructs a list of messages including text context and base64 images for Gemini.
    Strictly follows Multi-Vector Linking logic: retrieve 'image_path' from metadata.
    """
    context_docs = inputs["context"]
    question = inputs["question"]
    
    # System Message
    system_text = """You are an assistant for question-answering tasks. 
    Use the provided text context and attached images to answer the user's question.
    If you don't know the answer, just say that you don't know.
    Keep the answer concise.
    """
    
    # We build a list of content parts for the HumanMessage
    content_parts = []
    
    # Add Text Context
    context_str = "Context:\n"
    image_paths_processed = set()
    
    for i, doc in enumerate(context_docs):
        content = doc.page_content
        context_str += f"\n[Document {i}]\n{content}\n"
        
        # Check for images in metadata (Key: 'image_path' as per requirement)
        img_paths_val = doc.metadata.get("image_path", "[]")
        
        # Deserialize stringified list
        try:
            if isinstance(img_paths_val, str):
                if img_paths_val.startswith("["):
                    img_paths = ast.literal_eval(img_paths_val)
                else:
                    img_paths = [img_paths_val] # Fallback if single path string
            elif isinstance(img_paths_val, list):
                img_paths = img_paths_val
            else:
                img_paths = []
        except:
             img_paths = []

        if img_paths:
            for img_path in img_paths:
                if img_path and img_path not in image_paths_processed and os.path.exists(img_path):
                    # Encode Image for Gemini (Base64)
                    try:
                        with open(img_path, "rb") as image_file:
                            image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        })
                        image_paths_processed.add(img_path)
                    except Exception as e:
                        print(f"Error loading image {img_path}: {e}")

    # Add text content part
    final_text_prompt = f"{context_str}\n\nQuestion: {question}"
    content_parts.insert(0, {"type": "text", "text": final_text_prompt})
    
    messages = [
        SystemMessage(content=system_text),
        HumanMessage(content=content_parts)
    ]
    
    return messages

def get_chain():
    """
    Builds a Multimodal RetrievalQA chain using Gemini 3 Flash Preview.
    """
    # 1. Initialize LLM (Gemini Flash Latest - Stable & Fast)
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-flash-latest",
        google_api_key=GOOGLE_API_KEY,
        temperature=0
    )

    # 2. Get Retriever
    retriever = get_retriever()

    # 3. Chain
    chain = (
        {
            "context": retriever,
            "question": RunnableLambda(lambda x: x)
        }
        | RunnableLambda(multimodal_prompt_builder)
        | llm
        | StrOutputParser()
    )
    
    return chain
