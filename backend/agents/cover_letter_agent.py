"""LangGraph agent that generates a tailored, single-page cover letter.

Mirrors the resume generation agent:
    detect_language -> generate -> (review -> revise)* -> render -> measure
                                                            ^           |
                                                            +- condense +

The review loop (judge-only) runs only when ``enable_review`` is True.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import StateGraph, START, END

from models.cover_letter_response import CoverLetterResponse
from models.resume_review_verdict import ResumeReviewVerdict
from prompts.cover_letter_prompts import (
    get_cover_letter_prompt,
    get_cover_letter_reviewer_prompt,
    get_cover_letter_revise_prompt,
    get_cover_letter_condense_prompt,
)
from resume.mapper import ResumeMapper
from services.cv_factory import generate_cv, BASE_DIR
from services.llm_writer import groq_open_ai_client
from services.resume_review_service import count_pdf_pages

# Reuse the resume agent's primitives to avoid duplication.
from agents.resume_generation_agent import (
    MODEL,
    MAX_REVIEW_ITERATIONS,
    REVIEW_SCORE_THRESHOLD,
    detect_language,
    needs_revision,
    after_generate,
    _format_verdict_feedback,
)

logger = logging.getLogger(__name__)

TEMPLATE_NAME = "cover-letter.tex"
MAX_CONDENSE_ITERATIONS = 2

_FR_MONTHS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def _today_string(language: str) -> str:
    now = datetime.now()
    if language == "fr":
        return f"le {now.day} {_FR_MONTHS[now.month - 1]} {now.year}"
    return now.strftime("%B %d, %Y")


class LetterState(TypedDict):
    # Inputs
    job_description: str
    profile: Dict[str, Any]
    user_id: str
    output_file_name: str
    company: Optional[str]
    enable_review: bool

    # Working state
    language: str
    content: Optional[CoverLetterResponse]
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
def _call_llm(system_prompt: str, user_input: str) -> CoverLetterResponse:
    response = groq_open_ai_client.responses.parse(
        model=MODEL,
        temperature=0.3,
        instructions=system_prompt,
        input=user_input,
        text_format=CoverLetterResponse,
    )
    return response.output_parsed


def _user_input(state: LetterState, header: str) -> str:
    company_line = f"Target company: {state['company']}\n" if state.get("company") else ""
    return (
        f"{header}\n"
        f"{company_line}"
        f"Job offer (write the letter in this language):\n{state['job_description']}\n\n"
        f"Candidate profile (strict source of truth):\n{state['profile']}"
    )


def _generate_content(state: LetterState) -> CoverLetterResponse:
    return _call_llm(get_cover_letter_prompt(state["language"]), _user_input(state, "Write a cover letter."))


def _revise_content(state: LetterState) -> CoverLetterResponse:
    feedback = _format_verdict_feedback(state["review_verdict"] or {})
    system_prompt = get_cover_letter_revise_prompt(state["language"], feedback)
    current = state["content"].model_dump() if state["content"] else {}
    user_input = _user_input(state, "Improve this cover letter.") + f"\n\nPrevious version:\n{current}"
    return _call_llm(system_prompt, user_input)


def _condense_content(state: LetterState) -> CoverLetterResponse:
    system_prompt = get_cover_letter_condense_prompt(state["language"])
    current = state["content"].model_dump() if state["content"] else {}
    user_input = f"Letter to condense to one page:\n{current}"
    return _call_llm(system_prompt, user_input)


def _review_content(state: LetterState) -> ResumeReviewVerdict:
    system_prompt = get_cover_letter_reviewer_prompt(state["language"])
    current = state["content"].model_dump() if state["content"] else {}
    user_input = (
        f"Job offer:\n{state['job_description']}\n\n"
        f"Candidate profile (ground truth):\n{state['profile']}\n\n"
        f"Cover letter to evaluate:\n{current}"
    )
    response = groq_open_ai_client.responses.parse(
        model=MODEL,
        temperature=0.1,
        instructions=system_prompt,
        input=user_input,
        text_format=ResumeReviewVerdict,
    )
    return response.output_parsed


# --------------------------------------------------------------------------- #
# Context building / rendering
# --------------------------------------------------------------------------- #
def build_letter_context(content: CoverLetterResponse, profile: Dict[str, Any], company: Optional[str], language: str) -> Dict[str, Any]:
    profile_info = profile.get("profile") or {}
    location = ResumeMapper._compose_location(profile_info)

    contact_parts = [
        part
        for part in [
            location,
            profile_info.get("phone"),
            profile_info.get("email"),
        ]
        if part
    ]
    sender_contact = ResumeMapper.escape_latex(" | ".join(str(p) for p in contact_parts))

    return {
        "name": ResumeMapper.escape_latex(ResumeMapper._compose_name(profile_info)),
        "sender_contact": sender_contact,
        "recipient": ResumeMapper.escape_latex(company) if company else "",
        "date": ResumeMapper.escape_latex(_today_string(language)),
        "subject": ResumeMapper.escape_latex(content.subject),
        "salutation": ResumeMapper.escape_latex(content.salutation),
        "paragraphs": [ResumeMapper.escape_latex(p) for p in content.paragraphs],
        "closing": ResumeMapper.escape_latex(content.closing),
    }


def _render(state: LetterState) -> str:
    context = build_letter_context(state["content"], state["profile"], state.get("company"), state["language"])
    suffix = f"_v{state['iteration']}" if state["iteration"] > 0 else ""
    output_name = f"{state['output_file_name']}{suffix}"
    return generate_cv(output_name, context, user_id=state["user_id"], template_name=TEMPLATE_NAME)


# --------------------------------------------------------------------------- #
# Graph nodes
# --------------------------------------------------------------------------- #
def detect_language_node(state: LetterState) -> LetterState:
    state["language"] = detect_language(state["job_description"])
    return state


def generate_node(state: LetterState) -> LetterState:
    logger.info("[LETTER] Generating cover letter (%s)", state["language"])
    state["content"] = _generate_content(state)
    return state


def review_node(state: LetterState) -> LetterState:
    logger.info("[LETTER] Reviewing letter (review iteration %s)", state["review_iteration"])
    try:
        verdict = _review_content(state)
        state["review_verdict"] = verdict.model_dump()
        logger.info(
            "[LETTER] Review verdict: passed=%s score=%s grounded=%s issues=%s",
            verdict.passed, verdict.overall_score, verdict.grounded, len(verdict.issues),
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[LETTER] Review failed, accepting current content: %s", exc)
        state["review_verdict"] = {"passed": True, "overall_score": 0, "issues": []}
    return state


def revise_node(state: LetterState) -> LetterState:
    state["review_iteration"] += 1
    logger.info("[LETTER] Revising letter (review iteration %s)", state["review_iteration"])
    try:
        state["content"] = _revise_content(state)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[LETTER] Revise failed, keeping current content: %s", exc)
    return state


def render_node(state: LetterState) -> LetterState:
    state["pdf_path"] = _render(state)
    logger.info("[LETTER] Rendered PDF: %s (iteration %s)", state["pdf_path"], state["iteration"])
    return state


def measure_node(state: LetterState) -> LetterState:
    try:
        abs_path = (BASE_DIR / state["pdf_path"]).resolve()
        state["page_count"] = count_pdf_pages(str(abs_path))
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[LETTER] Could not measure pages: %s", exc)
        state["page_count"] = 1
    logger.info("[LETTER] Page count: %s", state["page_count"])
    return state


def condense_node(state: LetterState) -> LetterState:
    state["iteration"] += 1
    logger.info("[LETTER] Condensing letter (iteration %s)", state["iteration"])
    try:
        state["content"] = _condense_content(state)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("[LETTER] Condense failed, keeping current content: %s", exc)
    return state


def finalize_node(state: LetterState) -> LetterState:
    state["final_pdf_path"] = state["pdf_path"]
    logger.info("[LETTER] Done: %s (%s page(s))", state["final_pdf_path"], state["page_count"])
    return state


def needs_condensing(state: LetterState) -> str:
    if state["page_count"] <= 1:
        return "finalize"
    if state["iteration"] >= MAX_CONDENSE_ITERATIONS:
        logger.info("[LETTER] Max condense iterations reached, accepting overflow")
        return "finalize"
    return "condense"


def build_cover_letter_agent():
    graph = StateGraph(LetterState)
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
    graph.add_conditional_edges("generate", after_generate, {"review": "review", "render": "render"})
    graph.add_conditional_edges("review", needs_revision, {"revise": "revise", "render": "render"})
    graph.add_edge("revise", "review")
    graph.add_edge("render", "measure")
    graph.add_conditional_edges("measure", needs_condensing, {"condense": "condense", "finalize": "finalize"})
    graph.add_edge("condense", "render")
    graph.add_edge("finalize", END)
    return graph.compile()


def generate_cover_letter_with_agent(
    job_description: str,
    profile: Dict[str, Any],
    user_id: str,
    output_file_name: str,
    company: Optional[str] = None,
    enable_review: bool = False,
) -> Dict[str, Any]:
    """Run the cover letter agent and return the final PDF path + metadata."""
    logger.info(
        "[LETTER] Starting cover letter agent for user %s (review=%s)", user_id, enable_review
    )
    graph = build_cover_letter_agent()

    initial_state: LetterState = {
        "job_description": job_description or "",
        "profile": profile,
        "user_id": user_id,
        "output_file_name": output_file_name,
        "company": company,
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
        "review_iterations": result["review_iteration"],
        "review_verdict": result.get("review_verdict"),
    }
