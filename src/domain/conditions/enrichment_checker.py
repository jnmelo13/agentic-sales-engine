from ...application.schema.state import State
from langgraph.graph import END

def should_continue(state: State):
    """Check if enrichment should continue."""
    return (
        "enricher"
        if any(l.needs_enrichment() for l in state.filtered_leads)
        else END
    )