from langchain_openai import ChatOpenAI

from ..schema.state import State


def generate_summary(state: State, llm: ChatOpenAI) -> dict:
    """Generate natural language summary of results."""
    filtered = state.filtered_leads if hasattr(state, "filtered_leads") else []

    system_msg = {
        "role": "system",
        "content": f"""Summarize these B2B leads in a friendly way:
        Initial informations:
        {filtered}

        # Instructions
        - Use markdown to format the summary
        """,
    }

    messages = [system_msg] + state.messages
    response = llm.invoke(messages)

    return {
        "messages": [{"role": "assistant", "content": response.content}]
    }


def create_summary_node(llm: ChatOpenAI):
    """Create summary node with LLM dependency."""

    def node(state: State) -> dict:
        return generate_summary(state, llm)

    return node

