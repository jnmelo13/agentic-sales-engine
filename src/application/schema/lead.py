from typing import Optional

from pydantic import BaseModel, Field


class Lead(BaseModel):
    """Structured lead with enrichment fields."""

    company: str
    industry: str
    employee_count: int
    revenue_musd: float

    # Enrichment fields - initially None
    website: Optional[str] = None
    last_year_profit: Optional[float] = None
    last_quarter_ebitda: Optional[float] = None
    stock_variation_3m: Optional[float] = None

    def needs_enrichment(self) -> bool:
        """Check if lead still needs enrichment."""
        return (
            self.website is None
            or self.last_year_profit is None
            or self.last_quarter_ebitda is None
            or self.stock_variation_3m is None
        )


class LeadCompleted(BaseModel):
    """Completed lead with all enrichment fields."""

    company: str = Field(..., description="Name of the company")
    industry: str = Field(..., description="Industry sector of the company")
    employee_count: int = Field(..., description="Number of employees at the company")
    revenue_musd: float = Field(..., description="Annual revenue in millions of USD")
    website: str = Field(..., description="Official website URL of the company")
    last_year_profit: float = Field(
        ..., description="Company's profit for the last fiscal year in millions of USD"
    )
    last_quarter_ebitda: float = Field(
        ..., description="Company's EBITDA for the last quarter in millions of USD"
    )
    stock_variation_3m: float = Field(
        ..., description="Stock price variation over the last 3 months in percentage"
    )

