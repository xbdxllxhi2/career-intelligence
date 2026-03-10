"""Public API endpoints for jobs - no authentication required."""
from fastapi import APIRouter, Depends, Query

from .job_service import getJobs, getJobByReference, getFilterOptions
from .Job import JobBasic, JobDetail, FilterOptions
from .filters import JobFilters
from models.page import Page

import logging

router = APIRouter(prefix="/public/jobs", tags=["public-jobs"])

logger = logging.getLogger(__name__)


@router.get("/filters/options", summary="Get Filter Options", response_model=FilterOptions)
def get_filter_options_public():
    """Get available filter options for job search."""
    return getFilterOptions()


@router.get("", summary="Get Jobs (Public)", response_model=Page[JobBasic])
def get_jobs_public(
    filters: JobFilters = Depends(),
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
):
    """
    Get paginated list of jobs.
    Public endpoint - does not include user-specific data like application status.
    """
    return getJobs(user_id=None, filters=filters, page=page, size=size)


@router.get("/{reference}", summary="Get Job Details (Public)", response_model=JobDetail)
def get_job_by_reference_public(reference: str):
    """Get detailed information about a specific job."""
    return getJobByReference(reference=reference)
