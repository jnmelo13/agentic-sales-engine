import os
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis import RedisSaver

from src.application.schema.state import State
from src.application.graphs.builder import build_graph


def main():
    """Main entry point for Cloud Run / local execution."""
    load_dotenv(override=True)

    redis_uri = os.getenv("REDIS_URI")
    port = int(os.getenv("PORT", os.getenv("APP_PORT", 7860)))

    if not redis_uri:
        raise RuntimeError("REDIS_URI is not set")

    # Redis lifecycle = app lifecycle
    with RedisSaver.from_conn_string(redis_uri) as checkpointer:
        checkpointer.setup()

        # Build graph once
        llm = ChatOpenAI(model="gpt-4o-mini")
        graph = build_graph(llm, checkpointer)

        def chat(message, history):
            """Chat interface handler."""
            config = {
                "configurable": {
                    "thread_id": "2",
                    "user_id": "10",
                }
            }
            state = State(messages=[{"role": "user", "content": message}])
            result = graph.invoke(state, config=config)
            return result["messages"][-1].content

        # Start server
        gr.ChatInterface(
            chat,
            title="B2B Lead Generation Assistant",
            description="Ask me to find and qualify B2B leads!",
        ).launch(
            server_name="0.0.0.0",
            server_port=port,
        )


if __name__ == "__main__":
    main()
