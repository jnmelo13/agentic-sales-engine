from mem0 import MemoryClient
from typing import Optional
import os

class Mem0Service:
    """Long-term memory service using mem0."""
    
    def __init__(self):
        self.client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
    
    def add_memory(
        self, 
        messages: list[dict], 
        user_id: str,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Add memories from a conversation.
        mem0 automatically extracts relevant facts.
        """
        return self.client.add(
            messages=messages,
            user_id=user_id,
            metadata=metadata or {}
        )
    
    def search_memories(
        self, 
        query: str, 
        user_id: str, 
        limit: int = 5
    ) -> list[dict]:
        """Search for relevant memories."""
        results = self.client.search(
            query=query,
            filters={"user_id": user_id},
            limit=limit
        )
        return results.get("results", [])
    
    def update_memories(
        self,
       memory_id: str,
       new_memory: str
    ) -> list[dict]:
        """Update memories for a user."""
        return self.client.update(
            memory_id=memory_id,
            text=new_memory
        )
        
    def get_all_memories(self, user_id: str) -> list[dict]:
        """Get all memories for a user."""
        return self.client.get_all(user_id=user_id)
    
    def format_memories_for_context(self, memories: list[dict]) -> str:
        """Format memories as context for prompts."""
        if not memories:
            return ""
        
        memory_texts = [m.get("memory", "") for m in memories if m.get("memory")]
        if not memory_texts:
            return ""
            
        return "\n## Relevant Memories:\n" + "\n".join(f"- {m}" for m in memory_texts)