from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from ..agents.orchestrator_agent import create_orchestrator_node
from ..agents.lead_finder_agent import create_lead_finder_node
from ..agents.lead_screener_agent import lead_screener_node
from ..agents.data_enrichment_agent import create_enrichment_node, create_update_lead_node
from ..agents.summary_agent import create_summary_node

def register_nodes(graph: StateGraph, llm: ChatOpenAI,tools: list,):
    graph.add_node("chatbot", create_orchestrator_node(llm, tools))
    graph.add_node("tools", ToolNode(tools=tools))
    graph.add_node("search_tool", ToolNode(tools=tools))
    graph.add_node("search_tool_enricher", ToolNode(tools=tools))
    graph.add_node("lead_finder", create_lead_finder_node(llm, tools))
    graph.add_node("screener", lead_screener_node)
    graph.add_node("enricher", create_enrichment_node(llm, tools))
    graph.add_node("update_lead", create_update_lead_node(llm))
    graph.add_node("summary", create_summary_node(llm))