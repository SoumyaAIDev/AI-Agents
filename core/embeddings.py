import os
from dotenv import load_dotenv
import openai

load_dotenv()  


openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  


EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")  

def get_embeddings(texts):
    """
    Returns a list of embedding vectors for a list of input texts
    """
    if isinstance(texts, str):
        texts = [texts]  

    response = openai.Embedding.create(
        input=texts,
        engine=EMBEDDING_DEPLOYMENT_NAME  
    )

    return [record["embedding"] for record in response["data"]]
