import pdfplumber
from typing import List
from langchain_core.documents import Document
from utils import get_logger, clean_text

logger = get_logger(__name__)

def ingest_pdf(file_path: str) -> List[Document]:
    """
    Reads a single PDF file, extracts text page by page, and returns a list of Documents
    preserving page boundaries and metadata.
    """
    logger.info(f"Ingesting PDF: {file_path}")
    docs = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    cleaned_text = clean_text(text)
                    if cleaned_text:
                        docs.append(Document(
                            page_content=cleaned_text,
                            metadata={"page": page_num, "source": file_path}
                        ))
        logger.info(f"Successfully extracted {len(docs)} pages.")
        return docs
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        raise

def chunk_documents(docs: List[Document], chunk_size: int = 1500, chunk_overlap: int = 300) -> List[Document]:
    """
    Splits documents into smaller chunks while preserving metadata.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    logger.info(f"Chunking {len(docs)} documents (chunk_size={chunk_size}, overlap={chunk_overlap})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    logger.info(f"Created {len(chunks)} chunks.")
    return chunks
