import os
import uuid
import time
import streamlit as st
from dotenv import load_dotenv

from UI.agent import UIAgent
from core.mcp_bus import MCPBus, MCPMessage
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent
from langchain_openai import AzureOpenAIEmbeddings

# === Load .env ===
load_dotenv()

# === Load Embeddings ===
embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-3-large",
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# === MCP System Setup ===
mcp = MCPBus()
mcp.register("IngestionAgent", IngestionAgent(mcp))
mcp.register("RetrievalAgent", RetrievalAgent(mcp, embeddings))
mcp.register("LLMResponseAgent", LLMResponseAgent(mcp))

RESPONSES = {}

def ui_receive(msg):
    if msg.type == "FINAL_RESPONSE":
        RESPONSES[msg.trace_id] = msg.payload.get("answer", "⚠️ No answer found.")

ui_agent = UIAgent()
ui_agent.receive = ui_receive
mcp.register("UI", ui_agent)

# === Streamlit UI ===
st.title("🧠 Agentic RAG Chatbot")

# Upload
uploaded_files = st.file_uploader(
    "Upload documents (Max 200MB each)",
    type=["pdf", "docx", "pptx", "csv", "txt"],
    accept_multiple_files=True
)

file_paths = []
if uploaded_files:
    os.makedirs("data/uploads", exist_ok=True)
    for file in uploaded_files:
        size_mb = len(file.getvalue()) / (1024 * 1024)
        if size_mb > 200:
            st.error(f"❌ {file.name} is too large ({size_mb:.2f} MB). Limit is 200 MB.")
            continue

        path = f"data/uploads/{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        file_paths.append(path)

    if file_paths:
        trace_id = str(uuid.uuid4())
        mcp.send(MCPMessage(
            sender="UI",
            receiver="IngestionAgent",
            type="UPLOAD",
            trace_id=trace_id,
            payload={"files": file_paths}
        ))
        st.success("✅ Documents uploaded and processed.")

# === Query Section ===
query = st.text_input("Ask a question about the uploaded documents:")
submit = st.button("Submit Query")
answer_placeholder = st.empty()

if submit:
    if not file_paths:
        st.error("❌ Upload documents before querying.")
    elif not query.strip():
        st.error("❌ Enter a valid question.")
    else:
        trace_id = str(uuid.uuid4())
        mcp.send(MCPMessage(
            sender="UI",
            receiver="RetrievalAgent",
            type="QUERY",
            trace_id=trace_id,
            payload={"query": query.strip()}
        ))
        st.info("⏳ Query sent. Waiting for response...")

        
        for _ in range(20):  
            time.sleep(0.1)
            if trace_id in RESPONSES:
                break

        answer = RESPONSES.get(trace_id)
        if answer:
            answer_placeholder.success(f"💬 {answer}")
        else:
            answer_placeholder.warning("⚠️ No response received yet. Try again.")
