from langchain_core.tools import Tool
from src.infrastructure.memory.long_term.mem0.mem0_client import Mem0Service
import json

def create_search_memories_tool(mem0_service: Mem0Service, user_id: str) -> Tool:
    """Create search memories tool for long-term memory retrieval."""
    
    def search_memories(query: str) -> str:
        """
        Search long-term memory for relevant past interactions, user preferences,
        and historical context. Use this when you need to recall information from
        previous conversations.
        """

        memories = mem0_service.search_memories(
        query=query, 
        user_id=user_id,
        limit=5
         )
        
        if not memories:
            return "No relevant memories found."
        
        filtered_results = [
            {
                "id": memory.get("id"),
                "memory": memory.get("memory")
            }
            for memory in memories
        ]

        return json.dumps(filtered_results, indent=2)
    
    return Tool(
        name="search_memories",
        description=(
            "Search long-term memory for relevant past interactions, user preferences, "
            "and historical context. Use this when you need to recall information from "
            "previous conversations."
        ),
        func=search_memories,
    )