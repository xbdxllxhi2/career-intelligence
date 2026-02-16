import jobs.Job
import json
import uuid
import re
import unicodedata

from services.keyword_extractor import extract_keywords
from services.matcher import match_profile_sections
from services.llm_writer import generate_cv_section
from services.jobs_supplier import get_jobs
from services.profile_supplier import get_profile
from services.cv_factory import generate_cv, load_data
import logging
from jobs.Job import JobDetail
from models.llm_resume_generation_response import (
    ExperienceEntry,
    ProjectEntry,
    Skills,
    ResumeGenerationResponse,
)

logger = logging.getLogger(__name__)

LATEX_SPECIAL_CHARS = {
    "\\": r"\textbackslash{}",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "&": r"\&",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_LATEX_ESCAPE_RE = re.compile(r"([\\%$#&_{}~^])")

UNICODE_SPACES = r"[\u00A0\u2000-\u200B\u202F\u205F\u3000]"  # NBSP + various spaces
ZERO_WIDTH = r"[\u200B\u200C\u200D\uFEFF]"                  # zero-width chars

def normalize_llm_text(text: str) -> str:
    if text is None:
        return ""

    # Normalize compatibility forms (good default for CV content)
    text = unicodedata.normalize("NFKC", text)

    # Replace non-standard spaces with normal space
    text = re.sub(UNICODE_SPACES, " ", text)

    # Remove zero-width characters
    text = re.sub(ZERO_WIDTH, "", text)

    # Normalize runs of spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Keep newlines but prevent excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()



# def escape_latex(text: str) -> str:
#     for char, replacement in LATEX_SPECIAL_CHARS.items():
#         text = text.replace(char, replacement)
#     return text

def escape_latex(text: str) -> str:
    text = normalize_llm_text(text)
    return _LATEX_ESCAPE_RE.sub(lambda m: LATEX_SPECIAL_CHARS[m.group(1)], text)

def latex_safe_resume(resume: ResumeGenerationResponse) -> ResumeGenerationResponse:
    return ResumeGenerationResponse(
        objective=escape_latex(resume.objective),
        skills=Skills(
            technical=[escape_latex(s) for s in resume.skills.technical],
            soft=[escape_latex(s) for s in resume.skills.soft],
            tools=[escape_latex(s) for s in resume.skills.tools],
        ),
        experience=[
            ExperienceEntry(
                title=escape_latex(e.title),
                company=escape_latex(e.company),
                start_date=e.start_date,
                end_date=e.end_date,
                location=escape_latex(e.location),
                bullets=[escape_latex(b) for b in e.bullets],
            )
            for e in resume.experience
        ],
        projects=[
            ProjectEntry(
                title=escape_latex(p.title),
                url=p.url,
                description=escape_latex(p.description),
                # technologies=[escape_latex(t) for t in p.technologies],
                # link=p.link,  # URLs handled separately if needed
            )
            for p in resume.projects
        ],
    )


def generate_resume(job: JobDetail, profile):
    logger.info("Generating Resume...")
    keywords = extract_keywords(job.description)
    context = match_profile_sections(profile, keywords)
    logger.info("Context got after matching %s", context)

    context["job_description"] = job.description
    context["profile"] = profile
    resume_generated_reponse: ResumeGenerationResponse = latex_safe_resume(generate_cv_section(context))
    
    generated_resume_parts = resume_generated_reponse.model_dump()
    static_cv_parts = load_data()
    complete_cv = {**static_cv_parts, **generated_resume_parts}

    return generate_cv(job.reference, complete_cv)

def generate_resume_for_description(offer_description:str, profile):
    logger.info("Generating Resume for the given description...")
    keywords = extract_keywords(offer_description)
    context = match_profile_sections(profile, keywords)
    
    logger.info("Context got after matching %s", context)

    context["job_description"] = offer_description
    context["profile"] = profile
    resume_generated_reponse: ResumeGenerationResponse = latex_safe_resume(generate_cv_section(context))
    
    generated_resume_parts = resume_generated_reponse.model_dump()
    static_cv_parts = load_data()
    complete_cv = {**static_cv_parts, **generated_resume_parts}

    random_uuid = uuid.uuid4()
    return generate_cv(f'from_job_description_{random_uuid}', complete_cv)
    
