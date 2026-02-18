from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class JobBasic(BaseModel):  
    reference: str
    title: str
    seniority:Optional[str]=None
    company: Optional[str] = None
    company_description:Optional[str]=None
    company_type:Optional[str]=None
    company_website: Optional[str]=None
    company_founded_date:Optional[datetime]=None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    source:Optional[str]=None
    source_domain:Optional[str]=None
    has_direct_apply: Optional[bool]=None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    applied: bool = False


class JobDetail(JobBasic):
    job_url: Optional[str] = None
    description: Optional[str] = None
    source_apply_url: Optional[str] = None


class FilterOptions(BaseModel):
    countries: list[str]
    regions: list[str]
    cities: list[str]
    seniority_levels: list[str]
    sources: list[str]
    source_apply_url:Optional[str]=None
    company_employees_count:Optional[int]=None
    company_followers_count:Optional[int]=None
    description: Optional[str] = None
  
    
