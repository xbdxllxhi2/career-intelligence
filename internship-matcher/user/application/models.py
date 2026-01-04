from datetime import datetime
from typing import Optional
from grpc import Status
from pydantic import BaseModel


class CreateUserApplicationCommand(BaseModel):
    job_reference: str
    date: datetime
    portal: str
    rating: int
    notes: Optional[str] = None


class GetUserApplicationResponse(BaseModel):
    id: int
    job_reference: str
    job_title: str
    company: str
    date: datetime
    portal: str
    status: str
    notes: Optional[str] = None


class GetDetailedUserApplicationResponse(GetUserApplicationResponse):
    rating: int
    notes: str
    updated_at: str