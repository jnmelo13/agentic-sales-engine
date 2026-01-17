from typing import List, Dict, Any

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from ..schema.lead import Lead
from ..schema.state import State
from ...domain.interfaces.lead_repository import LeadRepository


def create_lead_storage_node(llm: ChatOpenAI, lead_repository: LeadRepository):
    """Returns an agent node function that handles lead storage and similarity checking.

    Args:
        llm: Language model to use
        lead_repository: Repository for storing and retrieving leads
    """

    async def process_leads(leads: List[Lead]) -> List[Dict[str, Any]]:
        """Process leads by storing them and finding similar ones.

        Args:
            leads: List of leads to process

        Returns:
            List of processed leads with storage and similarity information
        """
        processed_leads = []
        for lead in leads:
            # Store the lead
            lead_id = await lead_repository.store_lead(lead)
            
            # Check for similar leads
            similar_leads = await lead_repository.find_similar_leads(lead, limit=2)
            
            # Add similarity info
            similar_info = ""
            if similar_leads:
                similar_companies = [l.company for l in similar_leads if l.company != lead.company]
                if similar_companies:
                    similar_info = f" (Similar to: {', '.join(similar_companies)})"
            
            processed_leads.append({
                "id": lead_id,
                "lead": lead.model_dump(),
                "similar_info": similar_info
            })
        
        return processed_leads

    async def node(state: State) -> dict:
        """Process leads from state and store them with similarity checking.

        Args:
            state: Current state containing leads to process

        Returns:
            Updated state with processed leads and similarity information
        """
        # Get leads from state
        leads = [Lead(**lead) for lead in state.leads] if hasattr(state, "leads") else []
        
        if not leads:
            return {
                "messages": [
                    {"role": "assistant", "content": "No leads to process"}
                ]
            }

        # Process leads
        processed_leads = await process_leads(leads)

        # Create response message with similarity information
        lead_messages = []
        for pl in processed_leads:
            company = pl["lead"]["company"]
            similar_info = pl["similar_info"]
            lead_messages.append(f"- {company}{similar_info}")

        return {
            "leads": [pl["lead"] for pl in processed_leads],
            "messages": [
                {
                    "role": "assistant",
                    "content": "Processed leads:\n" + "\n".join(lead_messages)
                }
            ],
        }

    return node