import uuid
from typing import Any

from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.cv_factory import generate_cv
from services.resume_review_workflow import run_resume_review_workflow
from agents.resume_generation_agent import generate_resume_with_agent
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


def _generate_with_legacy_pipeline(user_id: str, job_description: str, profile, output_file_name: str) -> str:
    """Original pipeline: single-call generation + LangGraph review/optimization.

    Kept as a fallback for when the generation agent fails.
    """
    complete_cv: dict[str, Any] = _generate_resume_context(job_description, profile)
    pdf_path = generate_cv(output_file_name, complete_cv, user_id=user_id)

    logger.info("Running resume review and optimization workflow...")
    try:
        review_result = run_resume_review_workflow(
            pdf_path=pdf_path,
            cv_context=complete_cv,
            user_profile=profile,
            job_description=job_description,
            user_id=user_id,
            output_file_name=output_file_name,
        )
        return review_result["final_pdf_path"]
    except Exception as e:
        logger.error(f"Review workflow failed, returning original PDF: {e}")
        return pdf_path


def generate_resume_with_generation_agent(user_id: str, offer_description: str, profile, output_file_name: str | None = None):
    """Generate a single-page resume using the LangGraph generation agent.

    The agent detects the offer language, drafts content from the profile using
    few-shot reference resumes, and condenses until the PDF fits one page.
    """
    logger.info("Generating Resume with the generation agent...")
    if not output_file_name:
        output_file_name = f"agent_resume_{uuid.uuid4()}"

    result = generate_resume_with_agent(
        job_description=offer_description,
        profile=profile,
        user_id=user_id,
        output_file_name=output_file_name,
    )
    logger.info(
        "Agent resume generated: %s (lang=%s, pages=%s, condense=%s)",
        result["final_pdf_path"],
        result["language"],
        result["page_count"],
        result["condense_iterations"],
    )
    return result["final_pdf_path"]


def _generate(user_id: str, job_description: str, profile, output_file_name: str) -> str:
    """Primary resume generation: run the agent, fall back to the legacy pipeline."""
    try:
        return generate_resume_with_generation_agent(
            user_id, job_description, profile, output_file_name
        )
    except Exception as e:
        logger.error(f"Generation agent failed, falling back to legacy pipeline: {e}")
        return _generate_with_legacy_pipeline(user_id, job_description, profile, output_file_name)


def generate_resume(user_id: str, job: JobDetail, profile):
    logger.info("Generating Resume...")
    return _generate(user_id, job.description, profile, job.reference)


def generate_resume_for_description(user_id: str, offer_description: str, profile):
    logger.info("Generating Resume for the given description...")
    output_file_name = f"from_job_description_{uuid.uuid4()}"
    return _generate(user_id, offer_description, profile, output_file_name)
