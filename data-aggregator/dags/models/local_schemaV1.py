from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class Source(BaseModel):
    name: str
    source_domain: Optional[str]
    source_type: Optional[str]
    external_id: Optional[str]
    url: Optional[HttpUrl]
    fetched_at: Optional[datetime]


class Job(BaseModel):
    title: str
    job_checksum: str
    seniority: Optional[str]
    employment_type: List[str] = Field(default_factory=list)
    location_type: Optional[str] 
    url: Optional[HttpUrl]

    domain: Optional[str]
    description: str
    posted_at: Optional[datetime]
    expires_at: Optional[datetime]

    remote_type: Optional[str]
    is_remote: Optional[bool]
    has_easy_apply: Optional[bool]


class Organization(BaseModel):
    name: str

    logo: Optional[HttpUrl]
    industry: Optional[str]
    slogan: Optional[str]

    size_bucket: Optional[str]
    website: Optional[HttpUrl]
    description: Optional[str]

    type: Optional[str]

    employees: Optional[int]
    followers: Optional[int]

    founded_date: Optional[datetime]
    specialities: List[str] = Field(default_factory=list)


class Location(BaseModel):
    country: Optional[str]
    region: Optional[str]
    city: Optional[str]

    lat: Optional[float]
    lng: Optional[float]

    timezone: Optional[str]


class JobSchema(BaseModel):
    schema_version: str = Field(default="1.0.0")

    job_id: Optional[str]

    source: Source
    job: Job
    organization: Optional[Organization]
    location: Optional[Location]

    raw: Dict[str, Any] = Field(default_factory=dict)


