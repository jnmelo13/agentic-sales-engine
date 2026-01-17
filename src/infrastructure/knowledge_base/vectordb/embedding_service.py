"""
Service for generating lead embeddings.
"""
from typing import List
import numpy as np
import openai
from openai import AsyncClient

from src.application.schema.lead import Lead, LeadCompleted


class LeadEmbeddingService:
    """Service for generating and managing lead embeddings."""

    def __init__(self, api_key: str | None = None):
        """Initialize the embedding service.

        Args:
            api_key: Optional OpenAI API key. If not provided, uses environment variable.
        """
        self.client = AsyncClient(api_key=api_key)
        self.model = "text-embedding-3-small"
        self.dimensions = 64

    def _prepare_lead_text(self, lead: Lead | LeadCompleted) -> str:
        """Prepare lead data as text for embedding.

        Args:
            lead: The lead to prepare text for

        Returns:
            str: Text representation of the lead
        """
        text_parts = [
            f"Company: {lead.company}",
            f"Industry: {lead.industry}",
            f"Employees: {lead.employee_count}",
            f"Revenue: ${lead.revenue_musd}M USD",
        ]

        # Add enrichment fields if available
        if lead.website:
            text_parts.append(f"Website: {lead.website}")
        if lead.last_year_profit is not None:
            text_parts.append(f"Last Year Profit: ${lead.last_year_profit}M USD")
        if lead.last_quarter_ebitda is not None:
            text_parts.append(f"Last Quarter EBITDA: ${lead.last_quarter_ebitda}M USD")
        if lead.stock_variation_3m is not None:
            text_parts.append(f"3-Month Stock Variation: {lead.stock_variation_3m}%")
        if lead.contacts:
            contacts_text = "; ".join(
                f"{c.name} ({c.position})" for c in lead.contacts[:3]  # Limit to top 3 contacts
            )
            text_parts.append(f"Key Contacts: {contacts_text}")

        return " | ".join(text_parts)

    async def get_lead_embedding(self, lead: Lead | LeadCompleted) -> np.ndarray:
        """Generate embedding for a lead.

        Args:
            lead: The lead to generate embedding for

        Returns:
            np.ndarray: The embedding vector
        """
        text = self._prepare_lead_text(lead)
        
        response = await self.client.embeddings.create(
            input=[text],
            model=self.model,
            dimensions=self.dimensions,
        )
        
        return np.array(response.data[0].embedding)

    async def get_lead_embeddings(self, leads: List[Lead | LeadCompleted]) -> np.ndarray:
        """Generate embeddings for multiple leads in batch.

        Args:
            leads: List of leads to generate embeddings for

        Returns:
            np.ndarray: Array of embedding vectors
        """
        texts = [self._prepare_lead_text(lead) for lead in leads]
        
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model,
            dimensions=self.dimensions,
        )
        
        return np.array([item.embedding for item in response.data])