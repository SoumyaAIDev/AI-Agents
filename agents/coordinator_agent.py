from core.mcp_bus import MCPMessage

class CoordinatorAgent:
    def __init__(self, mcp):
        self.mcp = mcp
        self.session_state = {}

    def receive(self, message: MCPMessage):
        if message.type == "USER_UPLOAD":
        
            self.session_state[message.trace_id] = {"files": message.payload["files"]}
            self._dispatch_ingestion(message)

        elif message.type == "DOC_PARSED":
            
            self.session_state[message.trace_id]["chunks"] = message.payload["chunks"]
            self._dispatch_query(message.trace_id)

        elif message.type == "USER_QUERY":
            
            self.session_state[message.trace_id]["query"] = message.payload["query"]
            self._dispatch_query(message.trace_id)

        elif message.type == "RETRIEVAL_RESULT":
            self._dispatch_llm(message)

        elif message.type == "FINAL_RESPONSE":
            print(f"\n✅ Final Answer: {message.payload['answer']}\n")
            
    def _dispatch_ingestion(self, message: MCPMessage):
        self.mcp.send(MCPMessage(
            sender="CoordinatorAgent",
            receiver="IngestionAgent",
            type="UPLOAD",
            trace_id=message.trace_id,
            payload={"files": message.payload["files"]}
        ))

    def _dispatch_query(self, trace_id):
        query = self.session_state[trace_id].get("query")
        if not query:
            return  

        self.mcp.send(MCPMessage(
            sender="CoordinatorAgent",
            receiver="RetrievalAgent",
            type="QUERY",
            trace_id=trace_id,
            payload={"query": query}
        ))

    def _dispatch_llm(self, message: MCPMessage):
        self.mcp.send(MCPMessage(
            sender="CoordinatorAgent",
            receiver="LLMResponseAgent",
            type="RETRIEVAL_RESULT",
            trace_id=message.trace_id,
            payload=message.payload
        ))
