import os
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from utils import get_logger

logger = get_logger(__name__)

class QACitation(BaseModel):
    page_number: str = Field(description="Page number(s) where the answer was found, e.g., 'Page 4' or 'Pages 12-13'.")
    location_hint: str = Field(description="Clause, Article, or Section name/number if available.")
    supporting_snippet: str = Field(description="A brief 1-2 sentence verbatim snippet that directly backs up the answer.")

class QAResponse(BaseModel):
    answer: str = Field(description="The conversational answer to the user's question. If the document does not contain the answer, say so explicitly and explain what is missing.")
    citations: List[QACitation] = Field(description="List of exact citations supporting the answer. Should be empty if the answer is not found in the document.", default_factory=list)

def answer_question(query: str, vector_store: FAISS) -> QAResponse:
    """
    Performs RAG to answer a user's question, strictly grounded in the retrieved chunks.
    Ensures that citations are tied directly to the provided metadata.
    """
    logger.info(f"Answering query: {query}")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing.")

    # Retrieve relevant chunks
    # k=5 should cover most commercial lease inquiries without diluting context
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    retrieved_docs = retriever.invoke(query)

    if not retrieved_docs:
        logger.warning("No documents retrieved for the query.")
        return QAResponse(
            answer="I could not find any relevant information in the lease document to answer your question.",
            citations=[]
        )

    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", 
        temperature=0, 
        max_tokens=1000,
        openai_api_key=api_key, 
        openai_api_base="https://openrouter.ai/api/v1"
    )
    structured_llm = llm.with_structured_output(QAResponse)

    system_prompt = (
        "You are an expert AI lease analyzer assistent. You must answer the user's question using ONLY the provided document excerpts.\n"
        "RULES:\n"
        "1. Do not use outside knowledge. If the answer is not in the text, you must state that it cannot be answered from the lease and explain what info is missing.\n"
        "2. Provide strict citations for every factual claim you make.\n"
        "3. Your citations must include the 'page_number' (from the chunk metadata), 'location_hint' (like Article or Section if visible in the excerpt), and a 'supporting_snippet' (short verbatim quote)."
    )

    # Format retrieved contexts with their metadata
    context_parts = []
    for i, doc in enumerate(retrieved_docs, start=1):
        page = doc.metadata.get("page", "Unknown Page")
        context_parts.append(f"--- Excerpt {i} (Source: Page {page}) ---\n{doc.page_content}\n")
    
    full_context = "\n".join(context_parts)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Context Excerpts:\n{context}\n\nQuestion: {question}")
    ])

    chain = prompt | structured_llm

    try:
        logger.info(f"Sending {len(full_context)} characters of retrieved context to the LLM.")
        response = chain.invoke({
            "context": full_context,
            "question": query
        })
        logger.info("Successfully generated QA response.")
        return response
    except Exception as e:
        logger.error(f"QA failed: {e}")
        raise
