**📘 Agentic RAG Chatbot for Multi-Format Document QA using Model Context Protocol (MCP)**




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

**Agentic Design (MCP-driven):**



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


```
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
git clone https://github.com/SoumyaAIDev/AI-Agents.git
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
Q: "List top 10 smart contract hacks?"
A: "1. Alpha Homora Exploit (2021) - $37M stolen via Cream Finance due to an unsecured leveraged loop.
2. Uranium Finance Hack (2021) - $50M drained due to a bug in token swap logic during migration.
3. Poly Network Exploit (2021) - $610M stolen due to insecure owner verification in cross-chain contracts.
4. Cream Finance Hacks (2021) - Over $130M lost due to reentrancy and flash loan abuses.
5. BadgerDAO Frontend Attack (2021) - $120M drained from users due to a CDN hijack.
6. Wormhole Bridge Hack (2022) - $320M stolen due to missing guardian signature checks.
7. Ronin Network Hack (2022) - $625M stolen due to validator key compromise.
8. Nomad Bridge Exploit (2022) - ~$200M drained due to an initialization bug.
9. BNB Chain Hack (2022) - ~$570M in BNB created due to forged proofs.
10. Ankr Protocol Exploit (2022) - $5M+ drained due to a private key leak."
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
