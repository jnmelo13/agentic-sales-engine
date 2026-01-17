import uuid
import gradio as gr
from src.application.services.chat_service import ChatService


class GradioApp:
    """Gradio-based chat interface for the B2B agent."""

    def __init__(self, chat_service: ChatService) -> None:
        """
        Initialize the Gradio application.

        Args:
            chat_service: Service for handling chat interactions
        """
        self.chat_service = chat_service

    def _chat_handler(
        self, message: str, history: list, thread_id: str
    ) -> str:
        """
        Handle chat messages from Gradio interface.

        Args:
            message: User message
            history: Conversation history (managed by Gradio)
            thread_id: Thread ID for conversation tracking

        Returns:
            Assistant response
        """
        return self.chat_service.chat(message, thread_id)

    def launch(self, host: str, port: int) -> None:
        """
        Launch the Gradio chat interface.

        Args:
            host: Host address to bind to
            port: Port number to listen on
        """
        gr.ChatInterface(
            fn=self._chat_handler,
            title="B2B Lead Generation Assistant",
            description="Ask me to find and qualify B2B leads!",
            additional_inputs=[
                gr.Textbox(
                    label="Thread ID",
                    value=lambda: str(uuid.uuid4()),
                    interactive=True,
                )
            ],
        ).launch(
            server_name=host,
            server_port=port,
        )
