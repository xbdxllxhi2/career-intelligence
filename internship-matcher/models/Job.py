from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class JobBasic(BaseModel):
    reference: str
    title: str
    # org_description: Optional[str]
    company: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: Optional[datetime] = None


class JobDetail(JobBasic):
    job_url: Optional[str] = None
    expires_at: Optional[str] = None
    description: Optional[str] = None
