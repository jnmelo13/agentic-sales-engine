from ..schema.state import State


def triage(state: State) -> dict:
    """Filter leads based on qualification criteria."""
    print("TRIAGE")
    leads = state.leads if hasattr(state, "leads") else []

    filtered = []
    for lead in leads:
        if (
            lead.employee_count >= 0
            and lead.revenue_musd >= 0
            and lead.industry != "logistics"
        ):
            filtered.append(lead)

    print("=== FILTERED LEADS ===")
    for lead in filtered:
        print(lead)

    return {
        "filtered_leads": [lead.model_dump() for lead in filtered],
        "messages": [
            {
                "role": "assistant",
                "content": f"Filtered to {len(filtered)} qualified leads: {filtered}",
            }
        ],
    }


lead_screener_node = triage

