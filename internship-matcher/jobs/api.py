from fastapi import FastAPI, APIRouter, Query
from .job_service import getJobs, getJobByReference
from .Job import JobBasic, JobDetail
from models.page import Page

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", summary="Get Jobs", response_model=Page[JobBasic])
def root(page: int = Query(0, ge=0), size: int = Query(10, ge=1, le=100)):
    return getJobs(page=page, size=size)

@router.get("/{reference}", response_model=JobDetail)
def get_job_by_hash(reference: str):
    return getJobByReference(reference=reference)