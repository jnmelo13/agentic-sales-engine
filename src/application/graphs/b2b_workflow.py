from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from ..agents.lead_finder_agent import create_lead_finder_node
from ..agents.data_enrichment_agent import (
    create_enrichment_node,
    create_update_lead_node,
)
from ..agents.lead_screener_agent import lead_screener_node
from ..agents.orchestrator_agent import create_orchestrator_node
from ..agents.summary_agent import create_summary_node
from ..schema.state import State
from ..tools.search_tool import create_search_tool
from ...infrastructure.mcp_clients.client import get_mcp_client
from ..tools.retrieve_icp_tool import retrieve_icp_tool

def route_after_chatbot(state: State) -> str:
    """Route after chatbot based on next_action."""
    next_action = state.next_action
    print(f"Routing decision: {next_action}")
    return "lead_finder" if next_action == "find_leads" else END


def should_continue(state: State):
    """Check if enrichment should continue."""
    return (
        "enricher"
        if any(l.needs_enrichment() for l in state.filtered_leads)
        else END
    )


def build_graph(llm: ChatOpenAI | None = None) -> Any:
    """Build the B2B workflow graph."""
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini")

    read_icp_tool = retrieve_icp_tool(llm)

    # # Get MCP tools (async)
    # mcp_client = await get_mcp_client()
    # mcp_tools = await mcp_client.get_tools()

    # Non MCP tools
    tools = [create_search_tool()]
    tools_2 = [create_search_tool()]

    graph_builder = StateGraph(State)

    graph_builder.add_node("chatbot", create_orchestrator_node(llm, [read_icp_tool]))
    graph_builder.add_node("tools", ToolNode(tools=[read_icp_tool]))
    graph_builder.add_node("search_tool", ToolNode(tools=tools))
    graph_builder.add_node("search_tool_enricher", ToolNode(tools=tools_2))
    graph_builder.add_node("lead_finder", create_lead_finder_node(llm, tools))
    graph_builder.add_node("screener", lead_screener_node)
    graph_builder.add_node("enricher", create_enrichment_node(llm, tools_2))
    graph_builder.add_node("update_lead", create_update_lead_node(llm))
    graph_builder.add_node("summary", create_summary_node(llm))

    # Add conditional edge to route to tools when LLM calls a tool
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,  # This checks if there are tool calls in the response
        {
            "tools": "tools",  # Route to tools node if tool calls exist
            "__end__": "lead_finder",     # Otherwise end
        }
    )
    
    graph_builder.add_conditional_edges(
        "lead_finder",
        tools_condition,  # This checks if there are tool calls in the response
        {
            "tools": "search_tool",  # Route to tools node if tool calls exist
            "__end__": "screener",     # Otherwise end
        }
    )

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("search_tool", "lead_finder")
    graph_builder.add_edge("screener", "enricher")
    graph_builder.add_edge("summary", END)

    graph_builder.add_edge("search_tool_enricher", "enricher")

    # Conditional edges 
    graph_builder.add_conditional_edges(
        "enricher",
        tools_condition,
        {
            "tools": "search_tool_enricher",
            "__end__": "update_lead",
        },
    )

    graph_builder.add_conditional_edges(
        "update_lead",
        should_continue,
        {
            "enricher": "enricher",
            END: "summary",
        },
    )

    return graph_builder.compile()

