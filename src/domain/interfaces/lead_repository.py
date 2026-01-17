from abc import ABC, abstractmethod
from typing import List, Optional

from src.application.schema.lead import Lead, LeadCompleted


class LeadRepository(ABC):
    """Abstract base class for lead storage operations."""

    @abstractmethod
    async def store_lead(self, lead: Lead | LeadCompleted) -> str:
        """
        Store a lead in the repository.

        Args:
            lead: The lead to store, can be either a Lead or LeadCompleted instance

        Returns:
            str: The ID of the stored lead
        """
        pass

    @abstractmethod
    async def get_lead(self, lead_id: str) -> Optional[Lead | LeadCompleted]:
        """
        Retrieve a lead by its ID.

        Args:
            lead_id: The ID of the lead to retrieve

        Returns:
            Optional[Lead | LeadCompleted]: The lead if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_similar_leads(
        self, lead: Lead | LeadCompleted, limit: int = 5
    ) -> List[Lead | LeadCompleted]:
        """
        Find similar leads to the given lead.

        Args:
            lead: The lead to find similar leads for
            limit: Maximum number of similar leads to return

        Returns:
            List[Lead | LeadCompleted]: List of similar leads
        """
        pass

    @abstractmethod
    async def update_lead(self, lead_id: str, lead: Lead | LeadCompleted) -> bool:
        """
        Update an existing lead.

        Args:
            lead_id: The ID of the lead to update
            lead: The updated lead data

        Returns:
            bool: True if the lead was updated successfully, False otherwise
        """
        pass

    @abstractmethod
    async def delete_lead(self, lead_id: str) -> bool:
        """
        Delete a lead from the repository.

        Args:
            lead_id: The ID of the lead to delete

        Returns:
            bool: True if the lead was deleted successfully, False otherwise
        """
        pass