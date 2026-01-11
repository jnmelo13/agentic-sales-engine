import uuid
from langgraph.graph.state import CompiledStateGraph
from src.infrastructure.memory.long_term.mem0.mem0_client import Mem0Service

class ChatService:
    """Service for handling chat interactions with the B2B agent."""

    def __init__(
        self,
        graph: CompiledStateGraph,
        mem0_service: Mem0Service,
        default_user_id: str,
    ) -> None:
        """
        Initialize the chat service.

        Args:
            graph: Compiled LangGraph state graph
            mem0_service: Long-term memory service
            default_user_id: Default user ID for memory operations
        """
        self.graph = graph
        self.mem0_service = mem0_service
        self.default_user_id = default_user_id

    def chat(self, message: str, thread_id: str | None = None) -> str:
        """
        Process a chat message and return the response.

        Args:
            message: User message to process
            thread_id: Optional thread ID for conversation tracking

        Returns:
            Assistant response content
        """
        current_thread = thread_id if thread_id else str(uuid.uuid4())

        config = {
            "configurable": {
                "thread_id": current_thread,
                "user_id": self.default_user_id,
            }
        }

        state = {"messages": [{"role": "user", "content": message}]}

        result = self.graph.invoke(state, config=config)
        response_content = result["messages"][-1].content

        # Save to long-term memory
        self.mem0_service.add_memory(
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": response_content},
            ],
            user_id=self.default_user_id,
        )

        return response_content
