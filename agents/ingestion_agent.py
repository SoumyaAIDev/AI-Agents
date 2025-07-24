from core.document_parser import parse_file
from core.mcp_bus import MCPMessage
import os

class IngestionAgent:
    def __init__(self, mcp):
        self.mcp = mcp

    def receive(self, msg):
        if msg.type != "UPLOAD":
            return

        file_paths = msg.payload.get("files", [])
        trace_id = msg.trace_id
        all_chunks = []

        for file_path in file_paths:
            try:
                segments = parse_file(file_path)  
                content = "\n".join(segments).strip()  

                if not content:
                    print(f"⚠️ Empty content after parsing: {file_path}")
                    continue

                words = content.split()
                chunks = [
                    {
                        "content": " ".join(words[i:i+500]),
                        "metadata": {
                            "source": os.path.basename(file_path),
                            "file_path": file_path,
                            "chunk_id": idx
                        }
                    }
                    for idx, i in enumerate(range(0, len(words), 500))
                ]

                all_chunks.extend(chunks)
                print(f"✅ Parsed {len(chunks)} chunks from {file_path}")

            except Exception as e:
                print(f"❌ Error parsing {file_path}: {e}")

        if all_chunks:
            self.mcp.send(MCPMessage(
                sender="IngestionAgent",
                receiver="RetrievalAgent",
                type="CHUNKS",
                trace_id=trace_id,
                payload={"chunks": all_chunks}
            ))
            print(f"📨 Sent {len(all_chunks)} chunks to RetrievalAgent.")
        else:
            print("⚠️ No chunks to send.")
