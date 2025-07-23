from core.mcp_bus import MCPMessage

class UIAgent:
    def __init__(self):
        self.last_response = None  # Store last LLM answer or context

    def receive(self, msg: MCPMessage):
        print(f"📩 [UIAgent] Received from {msg.sender}: {msg.type}")
        self.last_response = msg.payload.get("answer") or msg.payload.get("context")
