import os
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.application.schema.state import State
from src.application.graphs.b2b_workflow import build_graph


def chat(message, history, graph):
    """Chat interface handler."""
    state = State(messages=[{"role": "user", "content": message}])
    result = graph.invoke(state)
    return result["messages"][-1].content


def main():
    """Main entry point for Cloud Run / local execution."""

    # Load secrets AFTER Cloud Run mounts them
    load_dotenv("/secrets/env", override=True)

    # Create LLM + Graph AFTER load_dotenv, and INSIDE main()
    llm = ChatOpenAI(model="gpt-4o-mini")
    graph = build_graph(llm)

    # Cloud Run PORT
    port = int(os.getenv("PORT", os.getenv("APP_PORT", 7860)))

    # Gradio server
    gr.ChatInterface(
        lambda m, h: chat(m, h, graph),
        title="B2B Lead Generation Assistant",
        description="Ask me to find and qualify B2B leads!",
    ).launch(
        server_name="0.0.0.0",
        server_port=port
    )


if __name__ == "__main__":
    main()
