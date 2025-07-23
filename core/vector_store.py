# core/vector_store.py

from langchain_community.vectorstores import FAISS
from langchain.schema import Document

class VectorDB:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vstore = None  # FAISS index

    def build(self, chunks):
        try:
            docs = [
                Document(page_content=chunk["content"], metadata=chunk.get("metadata", {}))
                for chunk in chunks
            ]
            self.vstore = FAISS.from_documents(docs, self.embeddings)
        except Exception as e:
            print(f"❌ Error building vector store: {e}")

    def search(self, query, k=4):
        if not self.vstore:
            print("⚠️ Vector store is empty.")
            return []
        return self.vstore.similarity_search(query, k=k)
