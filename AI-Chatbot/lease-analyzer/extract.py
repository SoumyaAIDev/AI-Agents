import os
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from utils import get_logger

logger = get_logger(__name__)

class Citation(BaseModel):
    page_number: Optional[int] = Field(description="Page number where the information is found. Extract this from the chunk metadata or context markers.")
    location_hint: Optional[str] = Field(description="Clause, Article, or Section number/title where the information resides.")
    supporting_snippet: Optional[str] = Field(description="A short verbatim snippet (1-2 sentences max) supporting the extraction.")

class ExtractedField(BaseModel):
    value: Optional[str] = Field(description="The extracted value in a readable string format. Null if not found.")
    field_type: Literal["Text", "Number", "Date", "Y-N", "Percentage", "Dropdown"] = Field(description="The basic data type of the field.")
    citations: List[Citation] = Field(default_factory=list, description="List of citations supporting this extracted value. Empty if not found.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0. 0.0 if not found.", ge=0.0, le=1.0)
    not_found_reason: Optional[str] = Field(description="If value is null, provide a short reason why it was not found, e.g., 'Not mentioned in document'.")

class LeaseSummary(BaseModel):
    tenant: ExtractedField = Field(description="The Entity or person renting the property.")
    landlord: ExtractedField = Field(description="The Owner or lessor of the property.")
    lease_start_date: ExtractedField = Field(description="When the lease term officially begins.")
    lease_end_date: ExtractedField = Field(description="When the lease term officially ends.")
    rent_amount: ExtractedField = Field(description="The base rent amount (e.g., monthly or annual).")
    renewal_options: ExtractedField = Field(description="Options for the tenant to extend the lease term.")
    termination_clauses: ExtractedField = Field(description="Conditions under which either party can terminate the lease early.")
    security_deposit: ExtractedField = Field(description="Amount required as a security deposit.")
    special_provisions: ExtractedField = Field(description="Any unique or specific conditions outside standard lease terms.")

def extract_lease_info(docs: List[Document]) -> LeaseSummary:
    """
    Extracts structured lease summary using a large context LLM.
    Passes the full document content to the LLM to get a single cohesive output.
    """
    logger.info("Starting schema-based extraction...")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing.")

    # Using an LLM with a large context window (128k) to process the entire lease document.
    # We use gpt-4o for complex extraction reliability, routed through OpenRouter.
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini", 
        temperature=0, 
        max_tokens=1500,
        openai_api_key=api_key, 
        openai_api_base="https://openrouter.ai/api/v1"
    )
    structured_llm = llm.with_structured_output(LeaseSummary)

    system_prompt = (
        "You are an expert commercial real estate paralegal. "
        "Your task is to carefully review the provided lease document text and extract specific material terms.\n"
        "For each requested field, provide the value, the type, the confidence score, and exact citations.\n"
        "IMPORTANT:\n"
        "- If a field cannot be found, set value to null, confidence to 0.0, and explain why in not_found_reason.\n"
        "- Citations must include the exact page number (found in the text markers like [Page X]) and a short verabtim snippet.\n"
        "- Be highly accurate and do not hallucinate."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Here is the lease document text:\n\n{context}"),
    ])

    # Construct context by adding distinct Page boundary markers
    context_parts = []
    for doc in docs:
        page = doc.metadata.get("page", "?")
        context_parts.append(f"--- [Page {page}] ---\n{doc.page_content}\n")
    
    full_context = "\n".join(context_parts)
    
    # We do not use an agent to iteratively extract due to latency and ease, structured output is deterministic.
    chain = prompt | structured_llm
    
    try:
        logger.info(f"Sending {len(full_context)} characters to the LLM for extraction.")
        result = chain.invoke({"context": full_context})
        logger.info("Extraction complete.")
        return result
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise
