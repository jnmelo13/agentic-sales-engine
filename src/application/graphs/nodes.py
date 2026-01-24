from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from ..agents.orchestrator_agent import create_orchestrator_node
from ..agents.lead_finder_agent import create_lead_finder_node
from ..agents.lead_screener_agent import lead_screener_node
from ..agents.data_enrichment_agent import create_enrichment_node, create_update_lead_node
from ..agents.summary_agent import create_summary_node
from ..agents.lead_storage_agent import create_lead_storage_node
from ...infrastructure.knowledge_base.vectordb.lead_storage import QDrantLeadStorage

def register_nodes(
    graph: StateGraph,
    llm: ChatOpenAI,
    orchestrator_tools: list,
    search_tools: list,
    lead_storage: QDrantLeadStorage,
) -> None:
    """Register the nodes for the graph.

    Args:
        graph: The state graph to register nodes on
        llm: Language model for agent nodes
        orchestrator_tools: Tools for the orchestrator (icp, memories)
        search_tools: Tools for search operations (company search)
        lead_storage: Shared lead storage instance
    """
    # Agent nodes
    graph.add_node("chatbot", create_orchestrator_node(llm, orchestrator_tools))
    graph.add_node("lead_finder", create_lead_finder_node(llm, search_tools))
    graph.add_node("screener", lead_screener_node)
    graph.add_node("enricher", create_enrichment_node(llm, search_tools))
    graph.add_node("update_lead", create_update_lead_node(llm))
    graph.add_node("summary", create_summary_node(llm))

    # Tool nodes - scoped by responsibility
    # Return errors as messages so LLM can handle auth flows
    graph.add_node("orchestrator_tools", ToolNode(tools=orchestrator_tools, handle_tool_errors=True))
    graph.add_node("search_tools", ToolNode(tools=search_tools, handle_tool_errors=True))
    graph.add_node("lead_storage", create_lead_storage_node(lead_storage))