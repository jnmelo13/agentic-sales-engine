from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI

from ..schema.lead import LeadCompleted
from ..schema.state import State


def enrich_leads(
    state: State, llm: ChatOpenAI, tools: list
) -> dict:
    """LLM decides if leads need enrichment using the search tool."""
    filtered = state.filtered_leads

    if not filtered:
        return {"filtered_leads": []}

    leads_needing_enrichment = [lead for lead in filtered if lead.needs_enrichment()]
    print("-" * 100)
    print(leads_needing_enrichment)
    print("-" * 100)

    if not leads_needing_enrichment:
        return {
            "messages": [{"role": "assistant", "content": "All leads have been enriched!"}]
        }

    lead_to_enrich = leads_needing_enrichment[0]

    last_message = state.messages[-1] if state.messages else None

    if isinstance(last_message, ToolMessage):
        print(f"✓ Tool results received for {lead_to_enrich.company}, proceeding to update...")
        return {
            "messages": [
                {"role": "assistant", "content": f"Processing results for {lead_to_enrich.company}"}
            ],
        }

    system_prompt = f"""You are enriching lead data for {lead_to_enrich.company}.

    Current data: {lead_to_enrich.model_dump_json()}

    Use search_company_info to find ONLY the missing fields. Be specific in your search query.
    After getting results, extract the relevant information clearly."""

    messages = state.messages + [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Find missing information for {lead_to_enrich.company}"},
    ]

    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response],
    }


def update_lead(state: State, llm: ChatOpenAI) -> dict:
    """Update lead with enriched data from search results."""
    print("UPDATE LEAD")
    lead_to_update = next((l for l in state.filtered_leads if l.needs_enrichment()), None)

    if not lead_to_update:
        return {}

    extractor = llm.with_structured_output(LeadCompleted)

    prompt = f"""
    Combine the existing lead and the search results, and output a full LeadCompleted object.

    Existing lead: {lead_to_update.model_dump_json()}
    Search results: {state.messages[-1].content}
    """

    enriched = extractor.invoke([{"role": "user", "content": prompt}])
    filtered = state.filtered_leads

    updated = [
        enriched.model_dump() if lead.company == enriched.company else lead.model_dump()
        for lead in filtered
    ]

    return {"filtered_leads": updated}


def create_enrichment_node(llm: ChatOpenAI, tools: list):
    """Create enrichment node with LLM and tools dependencies."""

    def node(state: State) -> dict:
        return enrich_leads(state, llm, tools)

    return node


def create_update_lead_node(llm: ChatOpenAI):
    """Create update lead node with LLM dependency."""

    def node(state: State) -> dict:
        return update_lead(state, llm)

    return node

