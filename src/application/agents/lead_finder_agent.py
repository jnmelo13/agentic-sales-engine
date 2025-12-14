from pydantic import BaseModel

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from ..schema.lead import Lead
from ..schema.state import State


def create_lead_finder_node(llm: ChatOpenAI, tools):
    """
    Returns an agent node function that uses LLM with tools to find leads matching the user's ICP.
    """

    def node(state: State) -> dict:
        # Get ICP from state
        icp = state.icp if hasattr(state, "icp") else None

        if icp:
            icp_info = f"\nUser's Ideal Customer Profile (ICP):\n{icp.model_dump_json()}\n"
        else:
            icp_info = "\nNo Ideal Customer Profile (ICP) available. Please retrieve it first.\n"

        system_prompt = (
            f"""You are a lead-finding agent.
            Use the following ICP to find matching leads:
            {icp_info}

            # Instructions
            - Use the available tools to find leads that match the ICP criteria
            - Find exactly 3 leads that match: industries, employee range, and regions from the ICP
            - Each lead must have: company name, industry, employee_count, and revenue_musd
            - Call tools to search for leads matching the ICP
            - Always look for contacts in the search results. If no contacts are found, leave the contacts field empty.
            """
        )

        messages = list(state.messages) if state.messages else []
        last_message = messages[-1] if messages else None

        # If tool just executed, extract leads from tool response using structured output
        if isinstance(last_message, ToolMessage):
            # Tool response received - parse it into Lead objects
            tool_content = str(last_message.content)

            # Use structured output to parse tool response into leads
            class LeadList(BaseModel):
                """List of leads extracted from tool response."""

                leads: list[Lead]

            # Parse tool response into structured leads
            parser = llm.with_structured_output(LeadList)
            prompt = f"""
            Extract leads from the following tool response.
            Convert the information into Lead objects with: company, industry, employee_count, revenue_musd.

            Tool Response:
            {tool_content}

            Extract exactly 3 leads that match the ICP criteria.
            """

            response = parser.invoke([{"role": "user", "content": prompt}])
            leads = response.leads if hasattr(response, "leads") else []

            return {
                "leads": [lead.model_dump() for lead in leads],
                "messages": [
                    {"role": "assistant", "content": f"Found {len(leads)} leads from tool results"}
                ],
            }

        # First call or continuing - add system message and bind tools
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages

        # Bind tools so LLM can call them
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(messages)

        return {
            "messages": [response],
        }

    return node

