from dataclasses import dataclass
from typing import Optional
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
import os

from .knowledge_base.vectordb.config import VectorDBSettings
from .knowledge_base.vectordb.embedding_service import LeadEmbeddingService
from .knowledge_base.vectordb.lead_storage import QDrantLeadStorage
from .clients.search_service import WebSearchService
from .memory.long_term.mem0.mem0_client import Mem0Service


@dataclass
class AppDependencies:
    llm: ChatOpenAI
    vector_db_settings: VectorDBSettings
    embedding_service: LeadEmbeddingService
    qdrant_client: QdrantClient
    lead_storage: QDrantLeadStorage
    web_search_service: WebSearchService
    mem0_service: Mem0Service
    memory_saver: Optional[any] = None
    user_id: Optional[str] = None


def create_dependencies(
    llm: Optional[ChatOpenAI] = None,
    memory_saver = None,
    mem0_service: Optional[Mem0Service] = None,
    user_id: Optional[str] = None,
) -> AppDependencies:
    """Create all application dependencies with proper configuration."""
    
    if llm is None:
        llm = ChatOpenAI(model="gpt-4o-mini")
    
    vector_db_settings = VectorDBSettings.from_env()
    embedding_service = LeadEmbeddingService()
    qdrant_client = QdrantClient(
        url=vector_db_settings.url,
        port=vector_db_settings.grpc_port if vector_db_settings.prefer_grpc else vector_db_settings.port,
        prefer_grpc=vector_db_settings.prefer_grpc,
        api_key=vector_db_settings.api_key,
        timeout=vector_db_settings.timeout,
    )
    lead_storage = QDrantLeadStorage(vector_db_settings, embedding_service)
    
    web_search_service = WebSearchService(api_key=os.getenv("SERPER_API_KEY"))
    
    if mem0_service is None:
        mem0_service = Mem0Service()
    
    return AppDependencies(
        llm=llm,
        vector_db_settings=vector_db_settings,
        embedding_service=embedding_service,
        qdrant_client=qdrant_client,
        lead_storage=lead_storage,
        web_search_service=web_search_service,
        mem0_service=mem0_service,
        memory_saver=memory_saver,
        user_id=user_id,
    )
