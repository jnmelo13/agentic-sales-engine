from langchain_openai import ChatOpenAI

from ..schema.state import State


def chatbot_node(old_state: State, llm: ChatOpenAI) -> dict:
    """Analyze user intent and route to appropriate workflow."""
    system_msg = {
        "role": "system",
        "content": "If user wants to find leads, respond with EXACTLY 'FIND_LEADS'. Otherwise chat normally.",
    }
    messages = [system_msg] + old_state.messages
    response = llm.invoke(messages)

    if "FIND_LEADS" in response.content:
        return {
            "messages": [
                {"role": "assistant", "content": "Great! Let me find some qualified leads for you..."}
            ],
            "next_action": "find_leads",
        }
    else:
        return {
            "messages": [{"role": "assistant", "content": response.content}],
            "next_action": "end",
        }


def create_orchestrator_node(llm: ChatOpenAI):
    """Create orchestrator node with LLM dependency."""

    def node(state: State) -> dict:
        return chatbot_node(state, llm)

    return node


orchestrator_node = None  # Will be set when LLM is available

