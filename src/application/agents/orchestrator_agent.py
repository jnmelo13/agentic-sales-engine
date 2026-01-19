import json

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from ..schema.icp import IdealCustomerProfile
from ..schema.state import State


def orchestrator_node(old_state: State, llm: ChatOpenAI, tools) -> dict:
    """Analyze user intent and route to appropriate workflow."""

    system_prompt = f"""
    You are a router agent that will route the user to the appropriate next step based on the user's intent.

    # Instructions
    - You can perform three main tasks: 
        1. Find NEW leads (requires ICP retrieval first)
        2. Search company information using web search
        3. Search EXISTING leads in the database
    - To find NEW leads, you must first retrieve the ICP (Ideal Customer Profile) using retrieve_icp tool
    - All new leads must be based on the ICP (Ideal Customer Profile)
    - To search EXISTING leads in the database, use the search_leads tool with a text query
    - You can use the following tools:
    {tools}
    - If you have already the ICP you must route to "lead_finder"

    # Examples
    <search_company_info_example>
    - User: What was the profit of the company ABCDE in 2024?
    - Assistant: I can help you with that. I will use the search_company_info tool to find the information.
    </search_company_info_example>

    <search_leads_example>
    - User: Do we have any fintech leads in the database?
    - Assistant: Let me search our database for fintech companies. [Uses search_leads tool with query "fintech companies"]
    </search_leads_example>

    <search_leads_example>
    - User: Show me software companies
    - Assistant: I'll search our stored leads for software companies. [Uses search_leads tool with query "software companies"]
    </search_leads_example>

    <find_new_leads_example>
    - User: Find me new leads
    - Assistant: I'll retrieve the ICP first. [Uses retrieve_icp tool, then routes to lead_finder]
    </find_new_leads_example>

    # Guardrails
    - If the user asks about EXISTING/STORED/CURRENT leads in the database, use search_leads tool
    - If the user asks to FIND NEW leads, use retrieve_icp then route to lead_finder
    - If the user asks about a specific company's information, use search_company_info tool
    - If the user doesn't want any of these, just continue the conversation
    - Keywords for search_leads: "do we have", "show me", "existing", "stored", "current", "in the database"
    - Keywords for find new leads: "find new", "generate leads", "discover leads"
    """

    # Get all messages first - always initialize
    messages = list(old_state.messages) if old_state.messages else []
    last_message = messages[-1] if messages else None

    # If tool just executed, check if it's the ICP tool response
    if isinstance(last_message, ToolMessage):
        if last_message.name == "retrieve_icp":
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

    # Filter the last 5 messages to not make the LLM confused
    recent_messages = messages[-5:] if len(messages) > 5 else messages
    routing_messages = [SystemMessage(content=system_prompt)] + recent_messages

    # Normal LLM invocation (messages is always defined at this point)
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(routing_messages)

    return {
        "messages": [response],
    }

def create_orchestrator_node(llm: ChatOpenAI, tools):
    """Create orchestrator node with LLM dependency."""

    def node(state: State) -> dict:
        return orchestrator_node(state, llm, tools)

    return node

