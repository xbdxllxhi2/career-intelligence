from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CreateUserApplicationCommand(BaseModel):
    job_reference: str
    date: datetime
    portal: str
    rating: int
    notes: Optional[str] = None


class GetUserApplicationResponse(BaseModel):
    id: int
    job_reference: Optional[str]=None
    job_title: str
    job_country: Optional[str]=None
    job_region: Optional[str]=None
    job_city: Optional[str]=None
    company: str
    company_logo_url:Optional[str]=None 
    date: datetime
    portal: str
    status: str
    notes: Optional[str] = None


class GetDetailedUserApplicationResponse(GetUserApplicationResponse):
    rating: int
    notes: str
    updated_at: str