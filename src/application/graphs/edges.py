from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from ...domain.conditions.enrichment_checker import should_continue
from ...domain.conditions.routing import chatbot_router, search_tools_router


def register_edges(graph: StateGraph) -> None:
    """Register the edges for the graph."""

    # Static edges
    graph.add_edge(START, "chatbot")
    graph.add_edge("orchestrator_tools", "chatbot")
    graph.add_edge("screener", "enricher")
    graph.add_edge("summary", END)

    # Conditional edges from chatbot
    graph.add_conditional_edges(
        "chatbot",
        chatbot_router,
        {
            "orchestrator_tools": "orchestrator_tools",
            "lead_finder": "lead_finder",
            "END": END,
        },
    )

    # Lead finder -> search_tools or screener
    graph.add_conditional_edges(
        "lead_finder",
        tools_condition,
        {
            "tools": "search_tools",
            "__end__": "screener",
        },
    )

    # Enricher -> search_tools or update_lead
    graph.add_conditional_edges(
        "enricher",
        tools_condition,
        {
            "tools": "search_tools",
            "__end__": "update_lead",
        },
    )

    # search_tools routes back to the agent that called it
    graph.add_conditional_edges(
        "search_tools",
        search_tools_router,
        {
            "lead_finder": "lead_finder",
            "enricher": "enricher",
        },
    )

    # Update lead continues enriching or moves to summary
    graph.add_conditional_edges(
        "update_lead",
        should_continue,
        {
            "enricher": "enricher",
            END: "summary",
        },
    )