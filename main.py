import os
from dotenv import load_dotenv
from core.mcp_bus import MCPBus
from agents.coordinator_agent import CoordinatorAgent
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent

def main():
    
    load_dotenv()

    
    mcp = MCPBus()

    
    mcp.register("CoordinatorAgent", CoordinatorAgent(mcp))
    mcp.register("IngestionAgent", IngestionAgent(mcp))
    mcp.register("RetrievalAgent", RetrievalAgent(mcp))
    mcp.register("LLMResponseAgent", LLMResponseAgent(mcp))

    print("✅ Agentic RAG Chatbot initialized with MCP.")
    print("🔄 Ready to receive messages... (UI handles interaction)")

if __name__ == "__main__":
    main()
