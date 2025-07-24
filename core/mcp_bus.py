class MCPMessage:
    def __init__(self, sender, receiver, type, trace_id, payload):
        self.sender = sender
        self.receiver = receiver
        self.type = type
        self.trace_id = trace_id
        self.payload = payload


class MCPBus:
    def __init__(self):
        self.registered_agents = {}  

    def register(self, name, agent):
        if not hasattr(agent, 'receive') or not callable(getattr(agent, 'receive')):
            raise TypeError(f"❌ Agent '{name}' must implement a callable `.receive(message)` method.")
        self.registered_agents[name] = agent
        agent.mcp = self  
        print(f"✅ [MCPBus] Registered agent '{name}'")

    def send(self, message: MCPMessage):
        receiver = self.registered_agents.get(message.receiver)

        if receiver is None:
            raise ValueError(f"❌ Receiver '{message.receiver}' is not registered in MCPBus. Available: {list(self.registered_agents.keys())}")
        
        if not hasattr(receiver, 'receive') or not callable(receiver.receive):
            raise TypeError(f"❌ Receiver '{message.receiver}' does not implement a callable `.receive(message)` method.")

        print(f"📨 [MCPBus] {message.sender} ➡️ {message.receiver} | type: {message.type} | trace_id: {message.trace_id}")
        receiver.receive(message)
