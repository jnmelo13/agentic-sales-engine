import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis import RedisSaver
import gradio as gr
from src.application.graphs.builder import build_graph
from src.infrastructure.memory.long_term.mem0.mem0_client import Mem0Service

DEFAULT_USER_ID = "10"

def main():
    """Main entry point for Cloud Run / local execution."""
    load_dotenv(override=True)

    redis_uri = os.getenv("REDIS_URI")
    port = int(os.getenv("PORT", os.getenv("APP_PORT", 7860)))

    if not redis_uri:
        raise RuntimeError("REDIS_URI is not set")

    with RedisSaver.from_conn_string(redis_uri) as checkpointer:
        checkpointer.setup()

        mem0_service = Mem0Service()

        llm = ChatOpenAI(model="gpt-4o-mini")
        graph = build_graph(llm, checkpointer,mem0_service, DEFAULT_USER_ID)

        def chat(message, history, thread_id):
            """Chat interface handler."""
            
            current_thread = thread_id if thread_id else str(uuid.uuid4())
            
            config = {
                "configurable": {
                    "thread_id": current_thread, 
                    "user_id": DEFAULT_USER_ID,
                }
            }
            
            state = {"messages": [{"role": "user", "content": message}]}
            
            result = graph.invoke(state, config=config)
            response_content = result["messages"][-1].content
            
            # Save to long-term memory
            mem0_service.add_memory(
                messages=[
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response_content}
                ],
                user_id=DEFAULT_USER_ID
            )
            
            return response_content

        gr.ChatInterface(
            fn=chat,
            title="B2B Lead Generation Assistant",
            description="Ask me to find and qualify B2B leads!",
            additional_inputs=[
                gr.Textbox(
                    label="Thread ID", 
                    value=lambda: str(uuid.uuid4()),
                    interactive=True
                )
            ]
        ).launch(
            server_name="0.0.0.0",
            server_port=port,
        )

if __name__ == "__main__":
    main()
