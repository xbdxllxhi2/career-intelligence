import models.Job
import json
from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.jobs_supplier import get_jobs
from services.profile_supplier import get_profile
from services.cv_factory import generate_cv, load_data
import logging
from models.Job import JobDetail

logger = logging.getLogger(__name__)

def generate_resume(job:JobDetail, profile):
    logger.info("Generating Cv...")
    keywords = extract_keywords(job.description)
    context = match_profile_sections(profile, keywords)
    logger.info("Context got after matching %s", context)

    cv_generated_text = generate_cv_section(context)    
    cv_generated_text = cv_generated_text.replace("%", r"\%")
    cv_generated_text_safe = cv_generated_text.replace("\\", "\\\\")

    generated_cv_parts = json.loads(cv_generated_text_safe)
    static_cv_parts = load_data()
    complete_cv = {**static_cv_parts, **generated_cv_parts}

    return generate_cv(job,complete_cv)
    
