# agents/llm_response_agent.py

import os
from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langchain_openai import AzureChatOpenAI
from core.mcp_bus import MCPMessage

load_dotenv()

class LLMResponseAgent:
    def __init__(self, mcp):
        self.mcp = mcp
        self.llm = AzureChatOpenAI(
            model_name="gpt-4o",
            azure_deployment=os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            temperature=0.2
        )

    def receive(self, msg: MCPMessage):
        if msg.type != "RETRIEVED_CONTEXT":
            return

        query = msg.payload.get("query", "").strip()
        chunks = msg.payload.get("chunks", [])

        if not query:
            answer = "⚠️ No question provided."
        elif not chunks:
            answer = "⚠️ No relevant context found to answer the question."
        else:
            context_text = "\n\n".join(chunk.get("content", "") for chunk in chunks)
            prompt = f"""You are a highly knowledgeable assistant. Use the context below to answer the question truthfully and concisely.

Context:
{context_text}

Question: {query}

Answer:"""

            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                answer = response.content.strip()
            except Exception as e:
                answer = f"❌ LLM error: {str(e)}"

        self.mcp.send(MCPMessage(
            sender="LLMResponseAgent",
            receiver="UI",
            type="FINAL_RESPONSE",
            trace_id=msg.trace_id,
            payload={"answer": answer}
        ))
