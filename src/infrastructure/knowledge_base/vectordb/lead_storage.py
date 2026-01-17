from typing import List, Optional, Dict, Any
import json
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from src.domain.interfaces.lead_repository import LeadRepository
from src.application.schema.lead import Lead, LeadCompleted
from .config import VectorDBSettings
from .embedding_service import LeadEmbeddingService


class QDrantLeadStorage(LeadRepository):
    """QDrant implementation of lead storage."""

    def __init__(
        self,
        settings: VectorDBSettings,
        embedding_service: LeadEmbeddingService,
    ):
        """Initialize QDrant lead storage.

        Args:
            settings: Vector database configuration
            embedding_service: Service for generating lead embeddings
        """
        self.settings = settings
        self.embedding_service = embedding_service
        self.client = QdrantClient(
            url=settings.url,
            port=settings.grpc_port if settings.prefer_grpc else settings.port,
            prefer_grpc=settings.prefer_grpc,
            api_key=settings.api_key,
            timeout=settings.timeout,
        )
        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """Ensure the leads collection exists with proper configuration."""
        try:
            self.client.get_collection(self.settings.collection_name)
        except Exception as e:
            print(f"Creating collection {self.settings.collection_name}")
            self.client.create_collection(
                collection_name=self.settings.collection_name,
                vectors_config=models.VectorParams(
                    size=self.settings.vector_size,
                    distance=self.settings.distance_metric,
                ),
            )

    def _lead_to_payload(self, lead: Lead | LeadCompleted) -> Dict[str, Any]:
        """Convert lead to QDrant payload."""
        return json.loads(lead.model_dump_json())

    def _payload_to_lead(self, payload: Dict[str, Any]) -> Lead | LeadCompleted:
        """Convert QDrant payload back to lead."""
        if all(
            field in payload
            for field in [
                "website",
                "last_year_profit",
                "last_quarter_ebitda",
                "stock_variation_3m",
                "contacts",
            ]
        ):
            return LeadCompleted(**payload)
        return Lead(**payload)

    async def store_lead(self, lead: Lead | LeadCompleted) -> str:
        """Store a lead in QDrant."""
        lead_id = str(uuid.uuid4())
        vector = await self.embedding_service.get_lead_embedding(lead)
        
        self.client.upsert(
            collection_name=self.settings.collection_name,
            points=[
                models.PointStruct(
                    id=lead_id,
                    vector=vector.tolist(),
                    payload=self._lead_to_payload(lead),
                )
            ],
        )
        return lead_id

    async def get_lead(self, lead_id: str) -> Optional[Lead | LeadCompleted]:
        """Retrieve a lead by its ID."""
        try:
            points = self.client.retrieve(
                collection_name=self.settings.collection_name,
                ids=[lead_id],
            )
            if not points:
                return None
            return self._payload_to_lead(points[0].payload)
        except UnexpectedResponse:
            return None

    async def find_similar_leads(
        self, lead: Lead | LeadCompleted, limit: int = 5
    ) -> List[Lead | LeadCompleted]:
        """Find similar leads using vector similarity search."""
        vector = await self.embedding_service.get_lead_embedding(lead)
        
        search_result = self.client.query_points(
            collection_name=self.settings.collection_name,
            query=vector.tolist(),
            with_payload=True,
            limit=limit,
        )
        
        for point in search_result.points:
            print(point.payload)

        return [self._payload_to_lead(point.payload) for point in search_result.points]

    async def update_lead(self, lead_id: str, lead: Lead | LeadCompleted) -> bool:
        """Update an existing lead."""
        try:
            vector = await self.embedding_service.get_lead_embedding(lead)
            
            self.client.upsert(
                collection_name=self.settings.collection_name,
                points=[
                    models.PointStruct(
                        id=lead_id,
                        vector=vector.tolist(),
                        payload=self._lead_to_payload(lead),
                    )
                ],
            )
            return True
        except UnexpectedResponse:
            return False

    async def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead from QDrant."""
        try:
            self.client.delete(
                collection_name=self.settings.collection_name,
                points_selector=models.PointIdsList(points=[lead_id]),
            )
            return True
        except UnexpectedResponse:
            return False