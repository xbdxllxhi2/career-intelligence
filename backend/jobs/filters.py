from typing import Optional
from pydantic import BaseModel


class JobFilters(BaseModel):
    title_contains: Optional[str] = None
    include_expired: bool = False
    has_easy_apply: Optional[bool] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
