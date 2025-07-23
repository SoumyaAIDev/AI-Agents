import os
from dotenv import load_dotenv
import openai

load_dotenv()  


openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., https://your-resource.openai.azure.com/
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # e.g., 2024-05-01

# Set deployment name of your embedding model
EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")  # e.g., "text-embedding-3-small"

def get_embeddings(texts):
    """
    Returns a list of embedding vectors for a list of input texts
    """
    if isinstance(texts, str):
        texts = [texts]  # Single string to list

    response = openai.Embedding.create(
        input=texts,
        engine=EMBEDDING_DEPLOYMENT_NAME  # Important: use 'engine' not 'deployment_name'
    )

    return [record["embedding"] for record in response["data"]]
