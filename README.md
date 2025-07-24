*📘 Agentic RAG Chatbot for Multi-Format Document QA using Model Context Protocol (MCP)*


**🚀 Overview**
  
  This project implements a modular Retrieval-Augmented Generation (RAG) chatbot powered by an agent-based architecture and Model Context Protocol (MCP). Users can upload documents in various formats, ask complex questions, and receive context-rich answers backed by retrieved document content.

**🧠 Core Features**

- ✅ Supports multi-format document ingestion: PDF, PPTX, DOCX, CSV, TXT/Markdown

- ✅ Agentic architecture with modular responsibilities

- ✅ MCP: In-memory message passing between agents

- ✅ Embedded vector search using FAISS/Chroma and OpenAI/HuggingFace embeddings

- ✅ Multi-turn QA with context-aware responses

- ✅ Web UI: Upload, chat, see sources


**🧱 Architecture**

***Agentic Design (MCP-driven):***

```
- flowchart LR
- A[User Uploads File / Asks Query]
- A --> B(IngestionAgent)
- B --> C(RetrievalAgent)
- C --> D(LLMResponseAgent)
- D --> A
```


1. **IngestionAgent:** Parses uploaded files into clean text chunks.
2. **RetrievalAgent:** Converts query into embedding → retrieves top-k matching chunks.
3. **LLMResponseAgent:** Forms prompt using query + chunks → gets answer from LLM.
4. **MCP (Model Context Protocol):** Message bus used by agents to pass structured context and results.

**🧾 Message Format (MCP)**
```
{
  "sender": "RetrievalAgent",
  "receiver": "LLMResponseAgent",
  "type": "RETRIEVED_CONTEXT",
  "trace_id": "abc-123",
  "payload": {
    "top_chunks": ["..."],
    "query": "What are the KPIs?"
  }
}
```

**⚙️ Tech Stack**

| **Layer**           | **Technology**                     |
|---------------------|------------------------------------|
| Frontend (UI)       | Streamlit / React                  |
| Backend Agents      | Python                             |
| Protocol            | In-memory Bus (MCP)                |
| Embeddings          | OpenAI / HuggingFace               |
| Vector Store        | FAISS / Chroma                     |
| Document Parsing    | PyMuPDF, python-docx, etc.         |

**📂 File Structure**

```YAML
.
├── app/                # Main UI & server
├── core/               # Common utilities (MCP, VectorDB)
├── agents/
│   ├── ingestion.py    # IngestionAgent
│   ├── retrieval.py    # RetrievalAgent
│   └── llm_response.py # LLMResponseAgent
├── data/               # Uploaded/parsed files
├── requirements.txt
├── README.md
└── run.py              # Entry point
```


🧪 Setup Instructions

```
# Clone repository
git clone https://github.com/yourusername/agentic-rag-chatbot.git
cd agentic-rag-chatbot

# Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run the app
python run.py
```


**🖥️ Usage**

1. Upload supported files (PDF, DOCX, CSV, etc.)

2. Ask questions in natural language

3. View generated answers + retrieved context chunks

**🧠 Sample Use Case**

```
Q: "Summarize the KPIs mentioned in the Q2 report."
A: "The KPIs mentioned are revenue growth (12%), customer retention (87%), and average deal size..."
```


**📌 Future Enhancements**
 
- Add LangChain Agent interface

- Replace in-memory bus with Kafka/NATS

- PDF highlighting with source

- Advanced UI chat history

**🤝 Contributing**

Contributions are welcome. Fork the repo, make changes, and open a PR.


**⚖️ License**

MIT License. See LICENSE file for details.
