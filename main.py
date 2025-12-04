import os
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.application.schema.state import State
from src.application.graphs.b2b_workflow import build_graph

llm = None
graph = None

def get_graph():
    """Lazily initialize LLM and Graph only on first request."""
    global llm, graph
    if graph is None:
        print("Initializing LLM + workflow graph...")
        llm = ChatOpenAI(model="gpt-4o-mini")
        graph = build_graph(llm)
    return graph

def chat(message, history):
    """Chat interface handler."""
    graph = get_graph()
    state = State(messages=[{"role": "user", "content": message}])
    result = graph.invoke(state)
    return result["messages"][-1].content

def main():
    """Main entry point for Cloud Run / local execution."""
    load_dotenv("/secrets/env", override=True)

    port = int(os.getenv("PORT", os.getenv("APP_PORT", 7860)))

    gr.ChatInterface(
        chat,
        title="B2B Lead Generation Assistant",
        description="Ask me to find and qualify B2B leads!",
    ).launch(
        server_name="0.0.0.0",
        server_port=port
    )

if __name__ == "__main__":
    main()
