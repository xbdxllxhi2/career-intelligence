"""LangGraph agent that generates a tailored, single-page resume.

Pipeline:
    detect_language -> generate -> render -> measure
                                     ^            |
                                     |     (> 1 page & iterations left)
                                     +-- condense +

The agent writes content in the language of the job offer, uses real resumes as
few-shot style references, and loops a condensing step until the rendered PDF
fits on a single A4 page (or a safety cap is reached).
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import StateGraph, START, END

from models.agent_resume_response import AgentResumeResponse
from models.resume_review_verdict import ResumeReviewVerdict
from prompts.resume_agent_prompts import (
    get_generation_prompt,
    get_condense_prompt,
    get_reviewer_prompt,
    get_revise_prompt,
)
from resume.mapper import ResumeMapper
from services.cv_factory import generate_cv, BASE_DIR
from services.llm_writer import groq_open_ai_client
from services.resume_review_service import count_pdf_pages

logger = logging.getLogger(__name__)

TEMPLATE_NAME = "resume-agent.tex"
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_CONDENSE_ITERATIONS = 3
MAX_REVIEW_ITERATIONS = 2
# Resume is accepted when the reviewer marks it passed, or its overall score
# reaches this threshold (avoids endless nitpicking loops).
REVIEW_SCORE_THRESHOLD = 8

# Localised section titles for the shared template.
LABELS = {
    "en": {
        "profile": "PROFILE",
        "skills": "TECHNICAL SKILLS",
        "experience": "PROFESSIONAL EXPERIENCE",
        "projects": "PROJECTS",
        "education": "EDUCATION",
        "additional": "ADDITIONAL INFORMATION",
        "project_link": "Project link",
        "languages": "Languages",
        "certifications": "Certifications",
    },
    "fr": {
        "profile": "PROFIL",
        "skills": "COMPÉTENCES TECHNIQUES",
        "experience": "EXPÉRIENCE PROFESSIONNELLE",
        "projects": "PROJETS",
        "education": "FORMATION",
        "additional": "INFORMATIONS COMPLÉMENTAIRES",
        "project_link": "Lien du projet",
        "languages": "Langues",
        "certifications": "Certifications",
    },
}

# Common French markers used for lightweight language detection.
_FR_MARKERS = re.compile(
    r"\b(le|la|les|des|une|un|et|pour|avec|vous|nous|dans|sur|stage|entreprise|"
    r"compétences|expérience|développeur|ingénieur|données|recherche|poste|"
    r"alternance|au sein|du|de la|notre|vos|ainsi)\b",
    re.IGNORECASE,
)
_EN_MARKERS = re.compile(
    r"\b(the|and|for|with|you|we|our|your|experience|skills|internship|team|"
    r"engineer|developer|data|looking|role|within|will|requirements|join)\b",
    re.IGNORECASE,
)


def detect_language(text: str) -> str:
    """Return 'fr' or 'en' based on simple marker frequency. Defaults to 'en'."""
    if not text:
        return "en"
    fr = len(_FR_MARKERS.findall(text))
    en = len(_EN_MARKERS.findall(text))
    # Accented characters are a strong French signal.
    fr += len(re.findall(r"[àâäéèêëîïôöùûüç]", text, re.IGNORECASE))
    detected = "fr" if fr > en else "en"
    logger.info("[AGENT] Language detection: fr=%s en=%s -> %s", fr, en, detected)
    return detected


class GenerationState(TypedDict):
    # Inputs
    job_description: str
    profile: Dict[str, Any]
    user_id: str
    output_file_name: str
    enable_review: bool

    # Working state
    language: str
    content: Optional[AgentResumeResponse]
    pdf_path: str
    page_count: int
    iteration: int

    # Review loop
    review_iteration: int
    review_verdict: Optional[Dict[str, Any]]

    # Output
    final_pdf_path: str


# --------------------------------------------------------------------------- #
# LLM calls
# --------------------------------------------------------------------------- #
def _call_llm(system_prompt: str, user_input: str) -> AgentResumeResponse:
    response = groq_open_ai_client.responses.parse(
        model=MODEL,
        temperature=0.2,
        instructions=system_prompt,
        input=user_input,
        text_format=AgentResumeResponse,
    )
    return response.output_parsed


def _generate_content(state: GenerationState) -> AgentResumeResponse:
    system_prompt = get_generation_prompt(state["language"])
    user_input = (
        f"Job offer (write the resume in this language):\n{state['job_description']}\n\n"
        f"Candidate profile (strict source of truth):\n{state['profile']}"
    )
    return _call_llm(system_prompt, user_input)


def _condense_content(state: GenerationState) -> AgentResumeResponse:
    overflow = max(state["page_count"], 2)
    system_prompt = get_condense_prompt(state["language"], overflow)
    current = state["content"].model_dump() if state["content"] else {}
    user_input = (
        f"Job offer:\n{state['job_description']}\n\n"
        f"Current resume content (condense this to fit one page):\n{current}"
    )
    return _call_llm(system_prompt, user_input)


def _review_content(state: GenerationState) -> ResumeReviewVerdict:
    system_prompt = get_reviewer_prompt(state["language"])
    current = state["content"].model_dump() if state["content"] else {}
    user_input = (
        f"Job offer:\n{state['job_description']}\n\n"
        f"Candidate profile (ground truth for fabrication checks):\n{state['profile']}\n\n"
        f"Resume to evaluate:\n{current}"
    )
    response = groq_open_ai_client.responses.parse(
        model=MODEL,
        temperature=0.1,  # deterministic judging
        instructions=system_prompt,
        input=user_input,
        text_format=ResumeReviewVerdict,
    )
    return response.output_parsed


def _format_verdict_feedback(verdict: Dict[str, Any]) -> str:
    """Turn a verdict dict into a concise feedback block for the revise prompt."""
    lines = [verdict.get("summary", "").strip()]
    if not verdict.get("grounded", True):
        lines.append("- WARNING: remove any claim not supported by the profile.")
    for issue in verdict.get("issues", []):
        lines.append(
            f"- [{issue.get('severity')}] {issue.get('location')}: "
            f"{issue.get('issue')} -> {issue.get('suggestion')}"
        )
    return "\n".join(line for line in lines if line)


def _revise_content(state: GenerationState) -> AgentResumeResponse:
    feedback = _format_verdict_feedback(state["review_verdict"] or {})
    system_prompt = get_revise_prompt(state["language"], feedback)
    current = state["content"].model_dump() if state["content"] else {}
    user_input = (
        f"Job offer:\n{state['job_description']}\n\n"
        f"Candidate profile (strict source of truth):\n{state['profile']}\n\n"
        f"Previous resume version to improve:\n{current}"
    )
    return _call_llm(system_prompt, user_input)


# --------------------------------------------------------------------------- #
# Context building / rendering
# --------------------------------------------------------------------------- #
def _escape_list(items) -> list[str]:
    return [ResumeMapper.escape_latex(item) for item in (items or [])]


def build_template_context(content: AgentResumeResponse, profile: Dict[str, Any], language: str) -> Dict[str, Any]:
    """Map agent content + profile into the LaTeX template context (LaTeX-safe)."""
    profile_info = profile.get("profile") or {}
    location = ResumeMapper._compose_location(profile_info)

    skills = [
        {
            "category": ResumeMapper.escape_latex(cat.category),
            "skill_items": _escape_list(cat.items),
        }
        for cat in content.skills
        if cat.items
    ]

    experience = [
        {
            "title": ResumeMapper.escape_latex(exp.title),
            "company": ResumeMapper.escape_latex(exp.company),
            "start_date": ResumeMapper.escape_latex(exp.start_date),
            "end_date": ResumeMapper.escape_latex(exp.end_date) if exp.end_date else None,
            "location": ResumeMapper.escape_latex(exp.location) if exp.location else "",
            "context": ResumeMapper.escape_latex(exp.context) if exp.context else "",
            "bullets": _escape_list(exp.bullets),
        }
        for exp in content.experience
    ]

    projects = [
        {
            "title": ResumeMapper.escape_latex(proj.title),
            "subtitle": ResumeMapper.escape_latex(proj.subtitle) if proj.subtitle else "",
            "url": ResumeMapper.normalize_text(proj.url) if proj.url else "",
            "year": ResumeMapper.escape_latex(proj.year) if proj.year else "",
            "bullets": _escape_list(proj.bullets),
        }
        for proj in content.projects
    ]

    return {
        "labels": LABELS.get(language, LABELS["en"]),
        "name": ResumeMapper.escape_latex(ResumeMapper._compose_name(profile_info)),
        "headline": "",
        "city": ResumeMapper.escape_latex(location),
        "phone": ResumeMapper.escape_latex(profile_info.get("phone") or ""),
        "email": ResumeMapper.escape_latex(profile_info.get("email") or ""),
        "email_href": ResumeMapper.normalize_text(profile_info.get("email") or ""),
        "linkedin_href": ResumeMapper.normalize_text(profile_info.get("linkedin") or ""),
        "github_href": ResumeMapper.normalize_text(profile_info.get("github") or ""),
        "objective": ResumeMapper.escape_latex(content.objective),
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "education": ResumeMapper._build_dynamic_education(profile, location),
        "languages": ResumeMapper._build_dynamic_languages(profile),
        "certifications": ResumeMapper._build_dynamic_certifications(profile),
    }


def _render(state: GenerationState) -> str:
    """Render + compile the current content, returning the relative PDF path."""
    context = build_template_context(state["content"], state["profile"], state["language"])
    suffix = f"_v{state['iteration']}" if state["iteration"] > 0 else ""
    output_name = f"{state['output_file_name']}{suffix}"
    return generate_cv(output_name, context, user_id=state["user_id"], template_name=TEMPLATE_NAME)


# --------------------------------------------------------------------------- #
# Graph nodes
# --------------------------------------------------------------------------- #
def detect_language_node(state: GenerationState) -> GenerationState:
    state["language"] = detect_language(state["job_description"])
    return state


def generate_node(state: GenerationState) -> GenerationState:
    logger.info("[AGENT] Generating resume content (%s)", state["language"])
    content = _generate_content(state)
    # Trust the offer-based detection over the model's self-report if they differ.
    if content.language != state["language"]:
        logger.info(
            "[AGENT] Model reported language %s, keeping detected %s",
            content.language,
            state["language"],
        )
    state["content"] = content
    return state


def review_node(state: GenerationState) -> GenerationState:
    logger.info("[AGENT] Reviewing content (review iteration %s)", state["review_iteration"])
    try:
        verdict = _review_content(state)
        state["review_verdict"] = verdict.model_dump()
        logger.info(
            "[AGENT] Review verdict: passed=%s score=%s grounded=%s issues=%s",
            verdict.passed,
            verdict.overall_score,
            verdict.grounded,
            len(verdict.issues),
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[AGENT] Review step failed, accepting current content: %s", exc)
        state["review_verdict"] = {"passed": True, "overall_score": 0, "issues": []}
    return state


def revise_node(state: GenerationState) -> GenerationState:
    state["review_iteration"] += 1
    logger.info("[AGENT] Revising content (review iteration %s)", state["review_iteration"])
    try:
        state["content"] = _revise_content(state)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[AGENT] Revise step failed, keeping current content: %s", exc)
    return state


def after_generate(state: GenerationState) -> str:
    return "review" if state.get("enable_review") else "render"


def needs_revision(state: GenerationState) -> str:
    verdict = state.get("review_verdict") or {}
    passed = verdict.get("passed", True)
    score = verdict.get("overall_score", 0)
    grounded = verdict.get("grounded", True)

    if (passed or score >= REVIEW_SCORE_THRESHOLD) and grounded:
        return "render"
    if state["review_iteration"] >= MAX_REVIEW_ITERATIONS:
        logger.info("[AGENT] Max review iterations reached, accepting current content")
        return "render"
    return "revise"


def render_node(state: GenerationState) -> GenerationState:
    pdf_path = _render(state)
    state["pdf_path"] = pdf_path
    logger.info("[AGENT] Rendered PDF: %s (iteration %s)", pdf_path, state["iteration"])
    return state


def measure_node(state: GenerationState) -> GenerationState:
    try:
        abs_path = (BASE_DIR / state["pdf_path"]).resolve()
        state["page_count"] = count_pdf_pages(str(abs_path))
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[AGENT] Could not measure pages: %s", exc)
        state["page_count"] = 1
    logger.info("[AGENT] Page count: %s", state["page_count"])
    return state


def condense_node(state: GenerationState) -> GenerationState:
    state["iteration"] += 1
    logger.info("[AGENT] Condensing content (iteration %s)", state["iteration"])
    try:
        state["content"] = _condense_content(state)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[AGENT] Condense step failed, keeping current content: %s", exc)
    return state


def finalize_node(state: GenerationState) -> GenerationState:
    state["final_pdf_path"] = state["pdf_path"]
    logger.info(
        "[AGENT] Done: %s (%s page(s), %s condense iteration(s))",
        state["final_pdf_path"],
        state["page_count"],
        state["iteration"],
    )
    return state


def needs_condensing(state: GenerationState) -> str:
    if state["page_count"] <= 1:
        return "finalize"
    if state["iteration"] >= MAX_CONDENSE_ITERATIONS:
        logger.info("[AGENT] Max condense iterations reached, accepting overflow")
        return "finalize"
    return "condense"


def build_generation_agent():
    graph = StateGraph(GenerationState)
    graph.add_node("detect_language", detect_language_node)
    graph.add_node("generate", generate_node)
    graph.add_node("review", review_node)
    graph.add_node("revise", revise_node)
    graph.add_node("render", render_node)
    graph.add_node("measure", measure_node)
    graph.add_node("condense", condense_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "detect_language")
    graph.add_edge("detect_language", "generate")
    graph.add_conditional_edges(
        "generate",
        after_generate,
        {"review": "review", "render": "render"},
    )
    graph.add_conditional_edges(
        "review",
        needs_revision,
        {"revise": "revise", "render": "render"},
    )
    graph.add_edge("revise", "review")
    graph.add_edge("render", "measure")
    graph.add_conditional_edges(
        "measure",
        needs_condensing,
        {"condense": "condense", "finalize": "finalize"},
    )
    graph.add_edge("condense", "render")
    graph.add_edge("finalize", END)
    return graph.compile()


def generate_resume_with_agent(
    job_description: str,
    profile: Dict[str, Any],
    user_id: str,
    output_file_name: str,
    enable_review: bool = False,
) -> Dict[str, Any]:
    """Run the resume generation agent and return the final PDF path + metadata.

    When ``enable_review`` is True, a judge-only reviewer agent evaluates the
    drafted content (job alignment, impact, ATS keywords, fabrication) and the
    generator revises it (bounded by MAX_REVIEW_ITERATIONS) before rendering.
    """
    logger.info(
        "[AGENT] Starting resume generation agent for user %s (review=%s)",
        user_id,
        enable_review,
    )
    graph = build_generation_agent()

    initial_state: GenerationState = {
        "job_description": job_description or "",
        "profile": profile,
        "user_id": user_id,
        "output_file_name": output_file_name,
        "enable_review": enable_review,
        "language": "en",
        "content": None,
        "pdf_path": "",
        "page_count": 0,
        "iteration": 0,
        "review_iteration": 0,
        "review_verdict": None,
        "final_pdf_path": "",
    }

    result = graph.invoke(initial_state)
    return {
        "final_pdf_path": result["final_pdf_path"],
        "language": result["language"],
        "page_count": result["page_count"],
        "condense_iterations": result["iteration"],
        "review_iterations": result["review_iteration"],
        "review_verdict": result.get("review_verdict"),
    }
