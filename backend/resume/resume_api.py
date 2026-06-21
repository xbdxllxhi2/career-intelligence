from typing import Any, Optional
from fastapi import APIRouter, Body, Depends
from fastapi.responses import FileResponse
from fastapi_keycloak_middleware import get_user
from sqlalchemy.orm import Session

from .resume_service import (
    generate_resume,
    generate_resume_for_description,
    generate_resume_with_generation_agent,
)
from jobs.job_service import getJobByReference
from user.profile.service import UserProfileService
from user.profile.mapper import UserProfileMapper
from database import engine
from pydantic import BaseModel

router = APIRouter(prefix="/resume", tags=["resume"])


class GenerateRequest(BaseModel):
    job_reference: Optional[str]=None
    job_description: Optional[str]=None


def profile_to_resume_format(profile_model) -> dict:
    """Convert UserProfile model to the format expected by resume generation services."""
    # Flatten skills from categories to a single list
    all_skills = []
    for skill_category in profile_model.skills:
        all_skills.extend(skill_category.skills)
    
    return {
        "profile": {
            "first_name": profile_model.first_name,
            "last_name": profile_model.last_name,
            "phone": profile_model.phone,
            "email": profile_model.email,
            "city": profile_model.city,
            "country": profile_model.country,
            "linkedin": profile_model.linkedin,
            "github": profile_model.github,
            "location": f"{profile_model.city}, {profile_model.country}" if profile_model.city and profile_model.country else profile_model.city or profile_model.country or "",
            "summary": profile_model.summary,
        },
        "education": [
            {
                "degree": edu.degree,
                "school": edu.school or edu.institution,
                "institution": edu.institution or edu.school,
                "year": edu.year,
                "coursework": edu.coursework,
            }
            for edu in profile_model.education
        ],
        "skills": all_skills,
        "experience": [
            {
                "title": exp.title,
                "company": exp.company,
                "period": exp.period,
                "location": exp.location,
                "tags": exp.tags,
                "bullets": exp.bullets,
            }
            for exp in profile_model.experience
        ],
        "projects": [
            {
                "name": proj.name,
                "description": proj.description,
                "url": proj.url,
                "year": proj.year,
                "tags": proj.tags,
                "bullets": proj.bullets,
            }
            for proj in profile_model.projects
        ],
        "languages": profile_model.languages,
        "certifications": [
            {
                "name": cert.name,
                "issuer": cert.issuer,
                "date": cert.date,
                "credentialId": cert.credentialId,
                "url": cert.url,
            }
            for cert in profile_model.certifications
        ],
        "extra_curricular": profile_model.extra_curricular,
    }


@router.post("", summary="Generate a taiLored CV to the job")
def create_resume(
    payload: GenerateRequest,
    user: Any = Depends(get_user),
    db: Session = Depends(engine.get_db)
):
    user_id = user.user_id
    job_reference = payload.job_reference
    job_detail = getJobByReference(reference=job_reference)
    
    # Fetch user profile from database
    profile_service = UserProfileService(db)
    profile_entity = profile_service.get_profile(user_id)
    profile_model = UserProfileMapper.entity_to_model(profile_entity)
    user_profile = profile_to_resume_format(profile_model)

    user_resume_path = generate_resume(user_id, job_detail, user_profile)
    print(user_resume_path)
    return FileResponse(
        path=user_resume_path,
        media_type="application/pdf",
        filename=f"{job_detail.company}_CV.pdf",
    )


@router.post("/from/description", summary="Generate a taiLored CV to the job description")
def create_resume_from_description(
    payload: GenerateRequest,
    user: Any = Depends(get_user),
    db: Session = Depends(engine.get_db)
):
    user_id = user.user_id
    
    # Fetch user profile from database
    profile_service = UserProfileService(db)
    profile_entity = profile_service.get_profile(user_id)
    profile_model = UserProfileMapper.entity_to_model(profile_entity)
    user_profile = profile_to_resume_format(profile_model)

    user_resume_path = generate_resume_for_description(user_id, payload.job_description, user_profile)
    print(user_resume_path)
    return FileResponse(
        path=user_resume_path,
        media_type="application/pdf",
        filename=f"resume.pdf",
    )


@router.post("/agent", summary="Generate a single-page CV via the generation agent")
def create_resume_with_agent(
    payload: GenerateRequest,
    user: Any = Depends(get_user),
    db: Session = Depends(engine.get_db),
):
    """Generate a resume using the LangGraph agent.

    Accepts either a ``job_reference`` (looked up for its description) or a raw
    ``job_description``. The agent auto-detects the offer language.
    """
    user_id = user.user_id

    profile_service = UserProfileService(db)
    profile_entity = profile_service.get_profile(user_id)
    profile_model = UserProfileMapper.entity_to_model(profile_entity)
    user_profile = profile_to_resume_format(profile_model)

    job_description = payload.job_description
    filename = "resume.pdf"
    if payload.job_reference:
        job_detail = getJobByReference(reference=payload.job_reference)
        job_description = job_detail.description
        filename = f"{job_detail.company}_CV.pdf"

    user_resume_path = generate_resume_with_generation_agent(
        user_id, job_description, user_profile
    )
    print(user_resume_path)
    return FileResponse(
        path=user_resume_path,
        media_type="application/pdf",
        filename=filename,
    )