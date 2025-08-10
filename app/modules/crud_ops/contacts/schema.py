from pydantic import BaseModel
from typing import Optional
class ContactProperties(BaseModel):
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

    class Config:
        extra = "ignore"