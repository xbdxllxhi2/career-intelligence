import uuid
from typing import Any

from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.cv_factory import generate_cv
import logging
from jobs.Job import JobDetail
from resume.mapper import ResumeMapper

logger = logging.getLogger(__name__)


def _generate_resume_context(job_description: str, profile: dict[str, Any]) -> dict[str, Any]:
    keywords = extract_keywords(job_description)
    context = match_profile_sections(profile, keywords)
    logger.info("Context got after matching %s", context)

    context["job_description"] = job_description
    context["profile"] = profile

    generated_resume_response = ResumeMapper.latex_safe_resume(generate_cv_section(context))
    return ResumeMapper.build_complete_cv_context(profile, generated_resume_response)


def generate_resume(user_id: str, job: JobDetail, profile):
    logger.info("Generating Resume...")
    complete_cv:dict[str, Any] = _generate_resume_context(job.description, profile)
    return generate_cv(job.reference, complete_cv, user_id=user_id)

def generate_resume_for_description(user_id: str, offer_description:str, profile):
    logger.info("Generating Resume for the given description...")
    complete_cv:dict[str, Any] = _generate_resume_context(offer_description, profile)
    random_uuid = uuid.uuid4()
    return generate_cv(f'from_job_description_{random_uuid}', complete_cv, user_id=user_id)
    
