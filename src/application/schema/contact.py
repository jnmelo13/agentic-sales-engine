from pydantic import BaseModel, Field

class Contact(BaseModel):
    """Contact information for a company."""

    name: str = Field(..., description="Name of the contact person")
    email: str = Field(..., description="Email of the contact person")
    phone: str = Field(..., description="Phone number of the contact person")
    position: str = Field(..., description="Position of the contact person")