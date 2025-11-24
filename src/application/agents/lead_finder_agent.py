from ..schema.lead import Lead
from ..schema.state import State


def get_leads(state: State) -> dict:
    """Simulate finding leads."""
    leads = [
        Lead(
            company="Americanas S.A.",
            industry="Marketplace",
            employee_count=1200,
            revenue_musd=12.4,
        ),
        Lead(
            company="Grupo Madero",
            industry="food",
            employee_count=400,
            revenue_musd=0.1,
        ),
        Lead(
            company="Grupo Boticário",
            industry="Beauty & Personal Care",
            employee_count=250,
            revenue_musd=1,
        ),
    ]

    return {
        "leads": [lead.model_dump() for lead in leads],
        "messages": [{"role": "assistant", "content": f"Found {len(leads)} leads"}],
    }


lead_finder_node = get_leads

