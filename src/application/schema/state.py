from typing import Annotated, Any, Optional

from langgraph.graph.message import add_messages
from pydantic import BaseModel, field_validator

from .icp import IdealCustomerProfile
from .lead import Lead


class State(BaseModel):
    """Application state for the B2B workflow graph."""

    messages: Annotated[list, add_messages]
    leads: list[Lead] = []
    filtered_leads: list[Lead] = []
    next_action: str = ""
    icp: Optional[IdealCustomerProfile] = None
    tool_caller: str = ""  # Track which agent called tools for routing back

    @field_validator("leads", "filtered_leads", mode="before")
    @classmethod
    def validate_leads(cls, v: Any) -> list[Lead]:
        """Convert dicts to Lead objects."""
        if not v:
            return []
        if isinstance(v[0], dict):
            return [Lead(**lead) if isinstance(lead, dict) else lead for lead in v]
        return v

