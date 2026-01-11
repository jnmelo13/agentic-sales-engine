from ...application.schema.state import State


def chatbot_router(state: State) -> str:
    """Route from chatbot to appropriate next node."""
    last_message = state.messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "orchestrator_tools"
    if state.next_action:
        return state.next_action
    return "END"


def search_tools_router(state: State) -> str:
    """Route back from search_tools to the agent that called it."""
    return state.tool_caller if state.tool_caller else "lead_finder"