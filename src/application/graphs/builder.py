from langgraph.graph import StateGraph

from ..tools.search_tool import create_search_tool
from ..tools.search_leads_tool import create_search_leads_tool
from ..schema.state import State
from ..graphs.nodes import register_nodes
from ..graphs.edges import register_edges
from ..tools.retrieve_icp_tool import retrieve_icp_tool
from ..tools.search_memories_tool import create_search_memories_tool
from ...infrastructure.container import AppDependencies


def build_graph(dependencies: AppDependencies) -> StateGraph:
    """Build the B2B workflow graph.
    
    Args:
        dependencies: All required application dependencies
        
    Returns:
        Compiled state graph ready for execution
    """
    icp_tool = retrieve_icp_tool(dependencies.llm)
    search_tool = create_search_tool(dependencies.web_search_service)
    search_memories_tool = create_search_memories_tool(
        dependencies.mem0_service, 
        dependencies.user_id
    )
    search_leads_tool = create_search_leads_tool(
        dependencies.qdrant_client,
        dependencies.vector_db_settings,
        dependencies.embedding_service,
    )

    orchestrator_tools = [icp_tool, search_memories_tool, search_tool, search_leads_tool]
    search_tools = [search_tool]

    graph_builder = StateGraph(State)

    register_nodes(
        graph_builder,
        dependencies.llm,
        orchestrator_tools,
        search_tools,
        dependencies.lead_storage,
    )
    register_edges(graph_builder)

    final_graph = graph_builder.compile(checkpointer=dependencies.memory_saver)

    png_bytes = final_graph.get_graph().draw_mermaid_png()
    with open("graph_mermaid_diagram.png", "wb") as f:
        f.write(png_bytes)

    return final_graph