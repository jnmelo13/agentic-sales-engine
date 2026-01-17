import asyncio
from ..schema.lead import Lead
from ..schema.state import State
from ...infrastructure.knowledge_base.vectordb.config import VectorDBSettings
from ...infrastructure.knowledge_base.vectordb.lead_storage import QDrantLeadStorage
from ...infrastructure.knowledge_base.vectordb.embedding_service import LeadEmbeddingService


def create_lead_storage_node():
    """Returns a sync node that runs async Qdrant operations."""

    def node(state: State) -> dict:  # Sync function
        """Process leads and store them in vector database."""
        
        # Define async logic
        async def store_leads_async():
            # Initialize services
            settings = VectorDBSettings(
                host="localhost",
                port=6333,
                collection_name="leads-collection",
                distance_metric="Cosine",
                vector_size=64,
                timeout=10
            )
            
            embedding_service = LeadEmbeddingService()
            lead_storage = QDrantLeadStorage(settings, embedding_service)
            
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