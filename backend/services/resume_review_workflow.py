import logging
from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from pathlib import Path
import shutil

from services.resume_review_service import (
    extract_text_from_pdf,
    count_pdf_pages,
    analyze_resume_with_llm
)
from services.resume_optimizer_service import optimize_resume_content
from services.cv_factory import generate_cv
from resume.mapper import ResumeMapper

logger = logging.getLogger(__name__)

# Max iterations for optimization
MAX_OPTIMIZATION_ITERATIONS = 5


class ReviewWorkflowState(TypedDict):
    """State for the resume review and optimization workflow."""
    pdf_path: str
    cv_context: Dict[str, Any]
    user_profile: Dict[str, Any]
    job_description: str
    user_id: str
    output_file_name: str

    # Workflow tracking
    iteration: int
    page_count: int
    is_valid: bool
    review_issues: list
    optimization_applied: bool

    # Results
    final_pdf_path: str
    review_report: Dict[str, Any]
    optimization_summary: Dict[str, Any]


def extract_and_validate_node(state: ReviewWorkflowState) -> ReviewWorkflowState:
    """Extract text from PDF and validate structure."""
    logger.info(f"[REVIEW] Starting extraction and validation for {state['output_file_name']}")

    try:
        # Extract text and count pages
        pdf_text = extract_text_from_pdf(state["pdf_path"])
        page_count = count_pdf_pages(state["pdf_path"])

        # Analyze with LLM
        review_response = analyze_resume_with_llm(pdf_text, state["cv_context"])

        state["page_count"] = page_count
        state["is_valid"] = review_response.is_valid
        state["review_issues"] = [issue.model_dump() for issue in review_response.issues]

        logger.info(f"[REVIEW] Extraction complete: {page_count} pages, valid={state['is_valid']}")

        return state

    except Exception as e:
        logger.error(f"[REVIEW] Error in extract_and_validate: {e}")
        state["is_valid"] = False
        state["page_count"] = 1
        state["review_issues"] = []
        return state


def should_optimize(state: ReviewWorkflowState) -> str:
    """Decide if optimization is needed."""
    if state["is_valid"]:
        logger.info("[REVIEW] Resume is valid, skipping optimization")
        return "output"

    elif state["iteration"] >= MAX_OPTIMIZATION_ITERATIONS:
        logger.info(f"[REVIEW] Max iterations ({MAX_OPTIMIZATION_ITERATIONS}) reached")
        return "output"

    else:
        logger.info(f"[REVIEW] Resume needs optimization (iteration {state['iteration'] + 1})")
        return "optimize"


def optimize_content_node(state: ReviewWorkflowState) -> ReviewWorkflowState:
    """Optimize resume content to fix issues."""
    logger.info(f"[OPTIMIZE] Starting optimization iteration {state['iteration'] + 1}")

    try:
        # Get feedback from review
        issues_feedback = "\n".join(
            [f"- {issue.get('description', 'Unknown issue')}" for issue in state["review_issues"]]
        )
        feedback = f"Issues found:\n{issues_feedback}" if issues_feedback else "General optimization to fit on 1 page"

        # Optimize content
        optimized = optimize_resume_content(
            state["cv_context"],
            issues=state["review_issues"],
            feedback=feedback
        )

        # Update context with optimized values
        state["cv_context"]["objective"] = optimized.objective
        state["cv_context"]["skills"] = {
            "technical": optimized.skills.technical,
            "soft": optimized.skills.soft,
            "tools": optimized.skills.tools
        }
        state["cv_context"]["experience"] = [
            {
                "title": exp.title,
                "company": exp.company,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "location": exp.location,
                "bullets": exp.bullets
            }
            for exp in optimized.experience
        ]
        state["cv_context"]["projects"] = [
            {
                "title": proj.title,
                "url": proj.url,
                "description": proj.description
            }
            for proj in optimized.projects
        ]

        state["optimization_applied"] = True
        state["optimization_summary"] = {
            "iteration": state["iteration"] + 1,
            "improvements": optimized.improvements_made,
            "notes": optimized.optimization_notes
        }

        logger.info(f"[OPTIMIZE] Optimization complete: {len(optimized.improvements_made)} improvements")

        return state

    except Exception as e:
        logger.error(f"[OPTIMIZE] Error in optimization: {e}")
        state["optimization_summary"] = {
            "iteration": state["iteration"] + 1,
            "improvements": ["Optimization failed, keeping current content"],
            "notes": str(e)
        }
        return state


def regenerate_cv_node(state: ReviewWorkflowState) -> ReviewWorkflowState:
    """Regenerate PDF with optimized content."""
    logger.info(f"[REGENERATE] Regenerating CV with optimized content")

    try:
        # Apply LaTeX safety to the optimized skill and experience values
        escaped_context = state["cv_context"].copy()

        # Escape optimized objective
        escaped_context["objective"] = ResumeMapper.escape_latex(escaped_context.get("objective", ""))

        # Escape optimized skills
        if "skills" in escaped_context:
            escaped_context["skills"] = {
                "technical": [ResumeMapper.escape_latex(s) for s in escaped_context["skills"].get("technical", [])],
                "soft": [ResumeMapper.escape_latex(s) for s in escaped_context["skills"].get("soft", [])],
                "tools": [ResumeMapper.escape_latex(s) for s in escaped_context["skills"].get("tools", [])]
            }

        # Escape optimized experience bullets
        if "experience" in escaped_context:
            for exp in escaped_context["experience"]:
                exp["bullets"] = [ResumeMapper.escape_latex(b) for b in exp.get("bullets", [])]

        # Regenerate PDF with iteration suffix
        iteration_suffix = f"_opt_v{state['iteration'] + 1}" if state["iteration"] > 0 else ""
        output_name = f"{state['output_file_name']}{iteration_suffix}"

        pdf_path = generate_cv(
            output_name,
            escaped_context,
            user_id=state["user_id"]
        )

        state["pdf_path"] = pdf_path
        logger.info(f"[REGENERATE] New PDF generated: {pdf_path}")

        return state

    except Exception as e:
        logger.error(f"[REGENERATE] Error regenerating CV: {e}")
        # Keep the old PDF path on error
        return state


def revalidate_node(state: ReviewWorkflowState) -> ReviewWorkflowState:
    """Re-validate the regenerated resume."""
    logger.info(f"[REVALIDATE] Re-validating resume (iteration {state['iteration'] + 1})")

    try:
        pdf_text = extract_text_from_pdf(state["pdf_path"])
        page_count = count_pdf_pages(state["pdf_path"])
        review_response = analyze_resume_with_llm(pdf_text, state["cv_context"])

        state["page_count"] = page_count
        state["is_valid"] = review_response.is_valid
        state["review_issues"] = [issue.model_dump() for issue in review_response.issues]
        state["iteration"] += 1

        logger.info(f"[REVALIDATE] Re-validation complete: pages={page_count}, valid={state['is_valid']}")

        return state

    except Exception as e:
        logger.error(f"[REVALIDATE] Error in re-validation: {e}")
        state["iteration"] += 1
        state["is_valid"] = False
        return state


def output_node(state: ReviewWorkflowState) -> ReviewWorkflowState:
    """Prepare final output."""
    logger.info(f"[OUTPUT] Preparing final output")

    state["final_pdf_path"] = state["pdf_path"]
    state["review_report"] = {
        "page_count": state["page_count"],
        "is_valid": state["is_valid"],
        "issues": state["review_issues"],
        "iterations_completed": state["iteration"]
    }

    if not state["optimization_summary"]:
        state["optimization_summary"] = {
            "applied": False,
            "reason": "Resume was valid on first attempt"
        }

    logger.info(f"[OUTPUT] Final output ready: {state['final_pdf_path']}")
    return state


def build_review_workflow():
    """Build the LangGraph workflow for resume review and optimization."""

    workflow = StateGraph(ReviewWorkflowState)

    # Add nodes
    workflow.add_node("extract_validate", extract_and_validate_node)
    workflow.add_node("optimize", optimize_content_node)
    workflow.add_node("regenerate", regenerate_cv_node)
    workflow.add_node("revalidate", revalidate_node)
    workflow.add_node("output", output_node)

    # Add edges
    workflow.add_edge(START, "extract_validate")
    workflow.add_conditional_edges(
        "extract_validate",
        should_optimize,
        {"optimize": "optimize", "output": "output"}
    )
    workflow.add_edge("optimize", "regenerate")
    workflow.add_edge("regenerate", "revalidate")
    workflow.add_conditional_edges(
        "revalidate",
        should_optimize,
        {"optimize": "optimize", "output": "output"}
    )
    workflow.add_edge("output", END)

    return workflow.compile()


def run_resume_review_workflow(
    pdf_path: str,
    cv_context: Dict[str, Any],
    user_profile: Dict[str, Any],
    job_description: str,
    user_id: str,
    output_file_name: str
) -> Dict[str, Any]:
    """
    Execute the resume review and optimization workflow.

    Args:
        pdf_path: Path to the generated PDF
        cv_context: CV context data
        user_profile: User profile data
        job_description: Job description
        user_id: User ID
        output_file_name: Base name for output files

    Returns:
        Dictionary with final_pdf_path, review_report, and optimization_summary
    """
    logger.info(f"[WORKFLOW] Starting resume review workflow for user {user_id}")

    # Build graph (could be cached if needed for performance)
    graph = build_review_workflow()

    # Initialize state
    initial_state: ReviewWorkflowState = {
        "pdf_path": pdf_path,
        "cv_context": cv_context,
        "user_profile": user_profile,
        "job_description": job_description,
        "user_id": user_id,
        "output_file_name": output_file_name,
        "iteration": 0,
        "page_count": 1,
        "is_valid": False,
        "review_issues": [],
        "optimization_applied": False,
        "final_pdf_path": pdf_path,
        "review_report": {},
        "optimization_summary": {}
    }

    # Execute workflow
    result = graph.invoke(initial_state)

    logger.info(f"[WORKFLOW] Resume review workflow complete")

    return {
        "final_pdf_path": result["final_pdf_path"],
        "review_report": result["review_report"],
        "optimization_summary": result["optimization_summary"],
        "optimization_applied": result["optimization_applied"]
    }
