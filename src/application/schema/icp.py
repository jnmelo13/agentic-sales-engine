from typing import Optional

from pydantic import BaseModel


class IdealCustomerProfile(BaseModel):
    """Ideal Customer Profile criteria extracted from Google Sheets."""

    industries_allowed: Optional[list[str]] = None
    industries_blocked: Optional[list[str]] = None
    employee_min: Optional[int] = None
    employee_max: Optional[int] = None
    regions_allowed: Optional[list[str]] = None
    regions_blocked: Optional[list[str]] = None
    technologies_required: Optional[list[str]] = None
    buyer_personas: Optional[list[str]] = None
    excluded_personas: Optional[list[str]] = None

    @classmethod
    def parse_semicolon_list(cls, value: str) -> list[str]:
        """Parse semicolon-separated string into list."""
        if not value or not isinstance(value, str):
            return []
        return [item.strip() for item in value.split(";") if item.strip()]

