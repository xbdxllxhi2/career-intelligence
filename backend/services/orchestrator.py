import json
from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.jobs_supplier import get_jobs
from services.profile_supplier import get_profile
from services.cv_factory import generate_cv, load_data
import logging

logger = logging.getLogger(__name__)

def create_cv(job, profile):
    logger.info("Creating CV for job[title: %s, company: %s]", job["title"], job["organization"])

    description = job.get("description_text", "")
    keywords = extract_keywords(description)
    context = match_profile_sections(profile, keywords)
    print(f"Context got after matching {context}")

    cv_generated_text = generate_cv_section(context)    
    cv_generated_text = cv_generated_text.replace("%", r"\%")
    cv_generated_text_safe = cv_generated_text.replace("\\", "\\\\")

    generated_cv_parts = json.loads(cv_generated_text_safe)
    static_cv_parts = load_data()
    complete_cv = {**static_cv_parts, **generated_cv_parts}

    generate_cv(job.get("reference"),complete_cv)
