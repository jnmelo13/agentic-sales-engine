from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from ..tools.search_tool import create_search_tool
from ..schema.state import State
from ..graphs.nodes import register_nodes
from ..graphs.edges import register_edges
from ..tools.retrieve_icp_tool import retrieve_icp_tool
from ..services.search_service import WebSearchService
import os

def build_graph(llm: ChatOpenAI | None = None) -> StateGraph:
    """Build the B2B workflow graph."""
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini")

    # # Get MCP tools (async)
    # mcp_client = await get_mcp_client()
    # mcp_tools = await mcp_client.get_tools()

    # Non MCP tools
    icp_tool = [retrieve_icp_tool(llm)]
    tools = [create_search_tool(WebSearchService(api_key=os.getenv("SERPER_API_KEY")))]
    tools_2 = [create_search_tool(WebSearchService(api_key=os.getenv("SERPER_API_KEY")))]

    graph_builder = StateGraph(State)

    register_nodes(graph_builder, llm, icp_tool, tools, tools_2)
    register_edges(graph_builder)

    final_graph = graph_builder.compile()
    png_bytes = final_graph.get_graph().draw_mermaid_png()
    with open("graph_mermaid_diagram.png", "wb") as f:
        f.write(png_bytes)

    return final_graph