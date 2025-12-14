from ...application.schema.state import State

def chatbot_router(state: State) -> str:
    last_message = state.messages[-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    if state.next_action:
        return state.next_action
    return "END"