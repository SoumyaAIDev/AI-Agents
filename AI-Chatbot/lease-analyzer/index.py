import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import List
from utils import get_logger

logger = get_logger(__name__)

def build_vector_store(chunks: List[Document]) -> FAISS:
    """
    Builds a FAISS vector store from document chunks using OpenAI embeddings.
    """
    logger.info("Building vector store...")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set. Please set it in your environment or app settings.")
    
    # Using text-embedding-3-small as it is efficient and robust
    # Note: For embeddings, typically OpenAI directly is used, but we route through OpenRouter base if supported
    # If openrouter doesn't map embeddings well, you may still need a direct OAI key.
    # We will pass the api key to the standard OpenRouter OpenAI base.
    embeddings = OpenAIEmbeddings(
        model="openai/text-embedding-3-small", 
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1"
    )
    
    # Create the FAISS index
    if not chunks:
        raise ValueError("No document chunks provided to build vector store.")
        
    vector_store = FAISS.from_documents(chunks, embeddings)
    logger.info("Vector store successfully built.")
    return vector_store
