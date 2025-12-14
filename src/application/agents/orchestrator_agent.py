import json

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from ..schema.icp import IdealCustomerProfile
from ..schema.state import State


def chatbot_node(old_state: State, llm: ChatOpenAI, tools) -> dict:
    """Analyze user intent and route to appropriate workflow."""

    system_prompt = f"""
    You are a router agent that will route the user to the appropriate next step based on the user's intent.

    # Instructions
    - You can only perform one task: Find leads 
    - You can only find leads after use a tool to retrive the ICP (Ideal Customer Profile)
    - All leads must be based on the ICP (Ideal Customer Profile)
    - You can use the following tools to find the ICP (Ideal Customer Profile):
    {tools}
    - If you have already the ICP you must retrieve with "lead_finder"

    # Guardrails
    - If the user don't want to find leads, you should end the conversation saying "Sorry, I can only help with finding leads."
    """

    # Get all messages first - always initialize
    messages = list(old_state.messages) if old_state.messages else []
    last_message = messages[-1] if messages else None

    # If tool just executed, check if it's the ICP tool response
    if isinstance(last_message, ToolMessage):
        # Handle ICP object directly (or dict if serialized)
        content = last_message.content

        try:
            icp_dict = json.loads(content)
            icp = IdealCustomerProfile(**icp_dict)

            # Store ICP if we got it
            if icp:
                return {
                    "icp": icp,
                    "messages": [
                        {"role": "assistant", "content": "ICP retrieved and stored successfully!"}
                    ],
                    "next_action": "lead_finder",
                }
        except (json.JSONDecodeError, ValueError) as e:
            # If parsing fails, continue normal flow
            pass

        # For other tool responses, continue normal flow
        # Add system message if needed
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages
    else:
        # First call - add system message if needed
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages

    # Normal LLM invocation (messages is always defined at this point)
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response],
    }


def create_orchestrator_node(llm: ChatOpenAI, tools):
    """Create orchestrator node with LLM dependency."""

    def node(state: State) -> dict:
        return chatbot_node(state, llm, tools)

    return node

