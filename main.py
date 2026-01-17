import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.application.graphs.builder import build_graph
from src.application.services.chat_service import ChatService
from src.infrastructure.memory.long_term.mem0.mem0_client import Mem0Service
from src.infrastructure.memory.short_term.redis.redis_saver import get_redis_checkpointer
from src.presentation.gradio_app import GradioApp

DEFAULT_USER_ID = "10"


def main() -> None:
    """Main entry point for Cloud Run / local execution."""
    load_dotenv(override=True)

    redis_uri = os.getenv("REDIS_URI")
    port = int(os.getenv("PORT", os.getenv("APP_PORT", 7860)))

    if not redis_uri:
        raise RuntimeError("REDIS_URI is not set")

    with get_redis_checkpointer(redis_uri) as checkpointer:
        checkpointer.setup()

        mem0_service = Mem0Service()
        llm = ChatOpenAI(model="gpt-4o-mini")
        graph = build_graph(llm, checkpointer, mem0_service, DEFAULT_USER_ID)

        chat_service = ChatService(graph, mem0_service, DEFAULT_USER_ID)
        app = GradioApp(chat_service)
        app.launch(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
