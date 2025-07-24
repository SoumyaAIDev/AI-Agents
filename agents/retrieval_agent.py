from core.vector_store import VectorDB
from core.mcp_bus import MCPMessage

class RetrievalAgent:
    def __init__(self, mcp, embeddings):
        self.mcp = mcp
        self.vdb = VectorDB(embeddings)

    def receive(self, msg: MCPMessage):
        if msg.type == "CHUNKS":
            chunks = msg.payload.get("chunks", [])
            self.vdb.build(chunks)
            print(f"✅ Indexed {len(chunks)} chunks into vector store.")

        elif msg.type == "QUERY":
            query = msg.payload.get("query", "").strip()
            if not query:
                print("⚠️ Empty query received. Skipping.")
                return

            results = self.vdb.search(query)
            print(f"🔍 Retrieved {len(results)} relevant chunks.")

            top_k_chunks = [{"content": r.page_content} for r in results]

            
            self.mcp.send(MCPMessage(
                sender="RetrievalAgent",
                receiver="LLMResponseAgent",
                type="RETRIEVED_CONTEXT",
                trace_id=msg.trace_id,
                payload={
                    "query": query,
                    "chunks": top_k_chunks
                }
            ))
