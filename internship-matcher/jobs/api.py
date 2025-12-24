from fastapi import FastAPI, APIRouter
from services.job_service import getJobs, getJobByReference
from models.Job import JobDetail


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", summary="Get Jobs")
def root():
    return getJobs()

@router.get("/{reference}", response_model=JobDetail)
def get_job_by_hash(reference: str):
    return getJobByReference(reference=reference)