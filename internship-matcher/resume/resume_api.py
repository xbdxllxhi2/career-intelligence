from fastapi import APIRouter, Body
from fastapi.responses import FileResponse
from .resume_service import generate_resume
from jobs.job_service import getJobByReference
import json
from pydantic import BaseModel

router = APIRouter(prefix="/resume", tags=["resume"])


class GenerateRequest(BaseModel):
    job_reference: str


@router.post("", summary="Generate a taiLored CV to the job description")
def create_resume(payload: GenerateRequest):
    #creating resume
    job_reference= payload.job_reference
    job_detail = getJobByReference(reference=job_reference)
    with open("./input/context/profile.json", "r", encoding="utf-8") as f:
        user_profile = json.load(f)

    user_resume_path = generate_resume(job_detail,user_profile)
    print(user_resume_path)
    return FileResponse(
        path=user_resume_path,
        media_type="application/pdf",
        filename=f"{job_detail.company}_CV.pdf",
    )
