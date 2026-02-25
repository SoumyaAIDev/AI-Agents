# Lease Analyzer App

An end-to-end, single-document Lease Analyzer built with Python, Streamlit, LangChain, and OpenAI.

## Features

1. **Structured Extraction**: Automatically extracts material terms from a commercial lease directly into a Pydantic schema using GPT-4o, returning the value, data type, confidence score, and strict citations directly backed by page boundaries.
2. **Q&A Chat**: Provides a conversational RAG interface over the lease with strict source grounding and citation formatting.
3. **Robust Processing**: Employs `pdfplumber` for text extraction with explicit page boundaries, and chunking with `RecursiveCharacterTextSplitter`.

## Setup & Running

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variable**:
   Create a `.env` file in the root of the project and add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-...
   ```
   Alternatively, you can enter the key directly into the Streamlit app sidebar.

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Architecture

- **`ingest.py`**: Extracts text from the uploaded PDF page by page using `pdfplumber`, mapping text to page metadata. Falls back appropriately.
- **`index.py`**: Embeds text chunks via `text-embedding-3-small` and stores them in a memory-backed FAISS vector store.
- **`extract.py`**: Uses `gpt-4o` with structured output capabilities to generate deterministic schema outputs matching the `LeaseSummary` Pydantic model. We use the full context as large leases easily fit within modern 128k context limits, giving the LLM holistic visibility into dispersed material terms.
- **`qa.py`**: Performs standard RAG with `k=5` context window constraint and structured output responses to enforce strict, unhallucinated citations.
- **`app.py`**: Hosts the Streamlit frontend with modular tabs and robust session state logic for one-time initialization.

## Edge Case Analysis & Mitigations

1. **Ambiguous / Missing Fields**:
   - *Problem*: A lease might not explicitly state "Security Deposit" but might talk about "Guarantees".
   - *Mitigation*: The `ExtractedField` schema has `not_found_reason` and the field value falls back to `null`. The prompt instructs the LLM not to guess but rather cleanly fail to `null` with a clear explanation if not definitive.
2. **Conflicting Clauses**:
   - *Problem*: A summary or introductory page might disagree with the actual terms in Article 5.
   - *Mitigation*: Passing the full document context to `gpt-4o` for extraction allows it to weigh the entire document (and often, later definitive clauses override summaries). The LLM is directed to rely on definitive clauses and returns a confidence score indicating if conflicting info was found.
3. **Defined Terms / Nested Definitions**:
   - *Problem*: The "Lease Start Date" might be defined as "Commencement Date," which itself is "30 days after the execution of the Work Letter."
   - *Mitigation*: Emphasizing a large-context structured extraction as opposed to standard snippet-level RAG. A traditional RAG extraction struggles with finding referenced definitions in entirely different sections. The `gpt-4o` window lets the model walk the definition chain inherently.
4. **Multi-location Answers**:
   - *Problem*: For QA, answering "What are the tenant's insurance obligations?" might span 3 distinct Articles.
   - *Mitigation*: Vector retrieval asks for `k=5` chunks, giving a wide conceptual span. The `QAResponse` schema explicitly dictates `List[QACitation]` thereby supporting an array of dispersed page sources for a single cohesive answer string.
5. **Long Sections and Chunking Issues**:
   - *Problem*: A 3,000-word indemnification clause gets chopped in half by a naive text splitter, breaking grammar and context.
   - *Mitigation*: `RecursiveCharacterTextSplitter` respects paragraph limits (`\n\n` -> `\n` -> `.`) reducing the likelihood of slicing directly in the middle of a material sentence. An overlap of `300` characters is used to maintain context bleed.

## Limitations

- A very un-parseable scanned document without a selectable text layer will require OCR (like `pytesseract` or `Unstructured`), which is not integrated in this baseline for speed and dependency reduction.
- Extremely large leases (>128k tokens) will hit context exhaustion for `extract.py` and require Map-Reduce extraction workflows.
