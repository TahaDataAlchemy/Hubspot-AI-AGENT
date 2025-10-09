from pydantic import BaseModel
from typing import Optional, Union
class ContactProperties(BaseModel):
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

    class Config:
        extra = "ignore"

class UpdateContactArgs(BaseModel):
    contact_id: Union[int, str]
    email: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

    class Config:
        extra = "ignore"

class Search_by_query(BaseModel):
    query:str