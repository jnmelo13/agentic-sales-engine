from langchain_core.tools import tool, BaseTool
from src.infrastructure.memory.long_term.mem0.mem0_client import Mem0Service


def create_update_memories_tool(mem0_service: Mem0Service) -> BaseTool:
    """Create update memories tool for long-term memory update."""
    
    @tool
    def update_memories(memory_id: str, new_memory: str) -> str:
        """
        Update a specific memory in long-term storage.
        
        Args:
            memory_id: The unique ID of the memory to update (get this from search_memories results)
            new_memory: The new content to replace the existing memory with
        """
        mem0_service.update_memories(
            memory_id=memory_id, 
            new_memory=new_memory
        )   
        
        return "Memory updated successfully."
    
    return update_memories