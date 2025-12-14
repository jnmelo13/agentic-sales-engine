from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition
from ...domain.conditions.routing import chatbot_router
from ...domain.conditions.enrichment_checker import should_continue

def register_edges(graph: StateGraph):

    graph.add_edge(START, "chatbot")    
    graph.add_edge("tools", "chatbot")
    graph.add_edge("search_tool", "lead_finder")
    graph.add_edge("screener", "enricher")
    graph.add_edge("summary", END)

    graph.add_edge("search_tool_enricher", "enricher")

    graph.add_conditional_edges(
        "chatbot",
        chatbot_router,
        {
            "tools": "tools",
            "lead_finder": "lead_finder",
            "END": END,
        }
    )
    
    graph.add_conditional_edges(
        "lead_finder",
        tools_condition,
        {
            "tools": "search_tool",
            "__end__": "screener",
        }
    )

    graph.add_conditional_edges(
        "enricher",
        tools_condition,
        {
            "tools": "search_tool_enricher",
            "__end__": "update_lead",
        },
    )

    graph.add_conditional_edges(
        "update_lead",
        should_continue,
        {
            "enricher": "enricher",
            END: "summary",
        },
    )