import json
import asyncio
from langchain_core.tools import Tool
from qdrant_client import QdrantClient

from src.infrastructure.knowledge_base.vectordb.config import VectorDBSettings
from src.infrastructure.knowledge_base.vectordb.embedding_service import LeadEmbeddingService


def create_search_leads_tool(
    client: QdrantClient,
    settings: VectorDBSettings,
    embedding_service: LeadEmbeddingService,
) -> Tool:
    
    def search_leads(query: str) -> str:
        try:
            async def get_embedding():
                response = await embedding_service.client.embeddings.create(
                    input=[query],
                    model=embedding_service.model,
                    dimensions=embedding_service.dimensions,
                )
                return response.data[0].embedding
            
            query_vector = asyncio.run(get_embedding())
            
            search_result = client.query_points(
                collection_name=settings.collection_name,
                query=query_vector,
                with_payload=True,
                limit=10,
            )
            
            if not search_result.points:
                return json.dumps({
                    "status": "success",
                    "message": "No leads found.",
                    "results": []
                })
            
            results = [point.payload for point in search_result.points]
            
            return json.dumps({
                "status": "success",
                "message": f"Found {len(results)} lead(s).",
                "results": results
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Error searching leads: {str(e)}"
            })
    
    return Tool(
        name="search_leads",
        description=(
            "Search for leads in the vector database using semantic search. "
            "Just provide a text query like 'Fintech companies' or 'software companies with high revenue'. "
            "Returns similar companies based on the query."
        ),
        func=search_leads,
    )
