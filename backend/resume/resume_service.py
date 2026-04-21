import uuid
from typing import Any

from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.cv_factory import generate_cv
from services.resume_review_workflow import run_resume_review_workflow
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
    pdf_path = generate_cv(job.reference, complete_cv, user_id=user_id)

    # Run review and optimization workflow
    logger.info("Running resume review and optimization workflow...")
    try:
        review_result = run_resume_review_workflow(
            pdf_path=pdf_path,
            cv_context=complete_cv,
            user_profile=profile,
            job_description=job.description,
            user_id=user_id,
            output_file_name=job.reference
        )
        return review_result["final_pdf_path"]
    except Exception as e:
        logger.error(f"Review workflow failed, returning original PDF: {e}")
        return pdf_path

def generate_resume_for_description(user_id: str, offer_description:str, profile):
    logger.info("Generating Resume for the given description...")
    complete_cv:dict[str, Any] = _generate_resume_context(offer_description, profile)
    random_uuid = uuid.uuid4()
    output_file_name = f'from_job_description_{random_uuid}'
    pdf_path = generate_cv(output_file_name, complete_cv, user_id=user_id)

    # Run review and optimization workflow
    logger.info("Running resume review and optimization workflow...")
    try:
        review_result = run_resume_review_workflow(
            pdf_path=pdf_path,
            cv_context=complete_cv,
            user_profile=profile,
            job_description=offer_description,
            user_id=user_id,
            output_file_name=output_file_name
        )
        return review_result["final_pdf_path"]
    except Exception as e:
        logger.error(f"Review workflow failed, returning original PDF: {e}")
        return pdf_path
    
