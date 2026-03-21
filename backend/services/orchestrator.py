from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.cv_factory import generate_cv
from resume.mapper import ResumeMapper
import logging

logger = logging.getLogger(__name__)

def create_cv(job, profile):
    logger.info("Creating CV for job[title: %s, company: %s]", job["title"], job["organization"])

    description = job.get("description_text", "")
    keywords = extract_keywords(description)
    context = match_profile_sections(profile, keywords)
    context["job_description"] = description
    context["profile"] = profile
    logger.info("Context got after matching %s", context)

    generated_resume_response = ResumeMapper.latex_safe_resume(generate_cv_section(context))
    complete_cv = ResumeMapper.build_complete_cv_context(profile, generated_resume_response)

    output_name = job.get("reference") or job.get("checksum") or "generated_cv"
    generate_cv(output_name, complete_cv)
