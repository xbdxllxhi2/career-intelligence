from math import log

from fastapi import Depends, FastAPI, APIRouter, Query, HTTPException
from sqlalchemy.orm import Session

from .job_service import getJobs, getJobByReference, getFilterOptions
from .smart_search_service import get_smart_search_results
from .Job import JobBasic, JobDetail, FilterOptions
from .filters import JobFilters
from models.page import Page
from models.job_matching_response import JobMatchingResponse
from services.job_matching_service import get_job_matching
from user.profile.service import UserProfileService
from user.profile.mapper import UserProfileMapper
from database import engine

from typing import List

import logging

router = APIRouter(prefix="/jobs", tags=["jobs"])

logger = logging.getLogger(__name__)

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


@router.get("/{reference}/matching", summary="Get Job Matching Analysis", response_model=JobMatchingResponse)
def get_job_matching_analysis(
    reference: str,
    user_id: int = Query(1, description="User ID for profile lookup"),
    db: Session = Depends(engine.get_db)
):
    """
    Analyze how well a user's profile matches a job posting.
    Uses LLM to perform intelligent matching across education, experience, skills, etc.
    """
    # Get the job details
    logger.info(f"Analyzing job matching for job reference: {reference} and user_id: {user_id}")
    job = getJobByReference(reference=reference)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with reference {reference} not found")
    
    if not job.description:
        raise HTTPException(status_code=400, detail="Job has no description to analyze")
    
    # Get the user profile
    profile_service = UserProfileService(db)
    try:
        profile_entity = profile_service.get_profile(user_id)
        user_profile = UserProfileMapper.entity_to_model(profile_entity)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"User profile with id {user_id} not found")
    
    # Perform matching analysis
    matching_response = get_job_matching(
        job_reference=reference,
        job_description=job.description,
        user_profile=user_profile
    )
    
    return matching_response
