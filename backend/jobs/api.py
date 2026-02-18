from fastapi import Depends, FastAPI, APIRouter, Query
from .job_service import getJobs, getJobByReference, getFilterOptions
from .smart_search_service import get_smart_search_results
from .Job import JobBasic, JobDetail, FilterOptions
from .filters import JobFilters
from models.page import Page
from typing import List

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/filters/options", summary="Get Filter Options", response_model=FilterOptions)
def get_filter_options():
    return getFilterOptions()


@router.get("/smart-search", summary="Smart Search for Jobs", response_model=List[JobBasic])
def smart_search(user_profile_id: str = Query(None)):
    """Find relevant jobs for the user's profile using AI matching."""
    return get_smart_search_results(user_profile_id)


@router.get("", summary="Get Jobs", response_model=Page[JobBasic])
def root(
    filters: JobFilters = Depends(),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
):
    return getJobs(filters, page=page, size=size)


@router.get("/{reference}", response_model=JobDetail)
def get_job_by_hash(reference: str):
    return getJobByReference(reference=reference)
