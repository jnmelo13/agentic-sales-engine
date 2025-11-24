from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from ..agents.data_enrichment_agent import (
    create_enrichment_node,
    create_update_lead_node,
)
from ..agents.lead_collector_agent import lead_collector_node
from ..agents.lead_finder_agent import lead_finder_node
from ..agents.orchestrator_agent import create_orchestrator_node
from ..agents.summary_agent import create_summary_node
from ..schema.state import State
from ..tools.search_tool import create_search_tool


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

    tools = [create_search_tool()]

    graph_builder = StateGraph(State)

    # Create nodes
    graph_builder.add_node("chatbot", create_orchestrator_node(llm))
    graph_builder.add_node("lead_finder", lead_finder_node)
    graph_builder.add_node("triage", lead_collector_node)
    graph_builder.add_node("enricher", create_enrichment_node(llm, tools))
    graph_builder.add_node("tools", ToolNode(tools=tools))
    graph_builder.add_node("update_lead", create_update_lead_node(llm))
    graph_builder.add_node("summary", create_summary_node(llm))

    # Edges
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        route_after_chatbot,
        {
            "lead_finder": "lead_finder",
            END: END,
        },
    )
    graph_builder.add_edge("lead_finder", "triage")
    graph_builder.add_edge("triage", "enricher")

    graph_builder.add_conditional_edges(
        "enricher",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "update_lead",
        },
    )

    graph_builder.add_edge("tools", "enricher")

    graph_builder.add_conditional_edges(
        "update_lead",
        should_continue,
        {
            "enricher": "enricher",
            END: "summary",
        },
    )

    graph_builder.add_edge("summary", END)

    return graph_builder.compile()

