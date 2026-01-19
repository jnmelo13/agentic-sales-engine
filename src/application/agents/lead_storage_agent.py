import asyncio
from ..schema.state import State
from ...infrastructure.knowledge_base.vectordb.lead_storage import QDrantLeadStorage


def create_lead_storage_node(lead_storage: QDrantLeadStorage):
    """Returns a sync node that runs async Qdrant operations."""

    def node(state: State) -> dict:
        """Process leads and store them in vector database."""
        
        async def store_leads_async():
            leads = state.leads
            for lead in leads:
                print(f"Storing lead: {lead}")
                await lead_storage.store_lead(lead)
        
        # Run async code in sync context
        try:
            print("Storing leads in vector database...")
            asyncio.run(store_leads_async())
        except RuntimeError:
            # If event loop already running (e.g., in Gradio)
            print("RuntimeError: Event loop already running. Applying nest_asyncio.")
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(store_leads_async())
        
        print("Leads stored in vector database.")
        return {}

    return node