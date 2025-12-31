import jobs.Job
import json
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


def escape_latex(text: str) -> str:
    for char, replacement in LATEX_SPECIAL_CHARS.items():
        text = text.replace(char, replacement)
    return text


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
                description=escape_latex(p.description),
                # technologies=[escape_latex(t) for t in p.technologies],
                # link=p.link,  # URLs handled separately if needed
            )
            for p in resume.projects
        ],
    )


def generate_resume(job: JobDetail, profile):
    logger.info("Generating Cv...")
    keywords = extract_keywords(job.description)
    context = match_profile_sections(profile, keywords)
    logger.info("Context got after matching %s", context)

    context["job_description"] = job.description
    context["profile"] = profile
    resume_generated_reponse: ResumeGenerationResponse = latex_safe_resume(generate_cv_section(context))
    
    generated_resume_parts = resume_generated_reponse.model_dump()
    static_cv_parts = load_data()
    complete_cv = {**static_cv_parts, **generated_resume_parts}

    return generate_cv(job, complete_cv)
