import logging
import json
from typing import Dict, Any, List
from models.resume_optimization_response import ResumeOptimizationResponse
from models.llm_resume_generation_response import Skills, ExperienceEntry, ProjectEntry
from services.llm_writer import groq_open_ai_client
from prompts.prompts_bank import get_resume_optimization_prompt
from models.resume_review_response import ReviewIssue

logger = logging.getLogger(__name__)


def optimize_resume_content(
    context: Dict[str, Any],
    issues: List[ReviewIssue],
    feedback: str
) -> ResumeOptimizationResponse:
    """
    Optimize resume content by asking LLM to:
    1. Make it more concise to fit on 1 page
    2. Fix identified issues
    3. Improve impact and relevance
    """
    try:
        # Prepare issues summary
        issues_summary = ""
        if issues:
            critical_issues = [i for i in issues if i.severity == "critical"]
            warning_issues = [i for i in issues if i.severity == "warning"]

            if critical_issues:
                issues_summary += "CRITICAL ISSUES:\n"
                for issue in critical_issues[:5]:
                    issues_summary += f"- {issue.description}\n"

            if warning_issues:
                issues_summary += "\nWARNINGS:\n"
                for issue in warning_issues[:5]:
                    issues_summary += f"- {issue.description}\n"

        # Build context for LLM
        user_prompt = f"""Optimize this resume content to fit on 1 page with improvements:

CURRENT OBJECTIVE:
{context.get('objective', 'N/A')}

CURRENT SKILLS:
- Technical: {', '.join(context.get('skills', {}).get('technical', [])[:5])}
- Soft: {', '.join(context.get('skills', {}).get('soft', [])[:3])}
- Tools: {', '.join(context.get('skills', {}).get('tools', [])[:5])}

CURRENT EXPERIENCE ({len(context.get('experience', []))} entries):
{json.dumps(context.get('experience', []), indent=2)[:1000]}

CURRENT PROJECTS ({len(context.get('projects', []))} entries):
{json.dumps(context.get('projects', []), indent=2)[:1000]}

IDENTIFIED ISSUES TO FIX:
{issues_summary if issues_summary else "None - general optimization requested"}

FEEDBACK:
{feedback}

Generate optimized JSON with improved content that fits on 1 page."""

        response = groq_open_ai_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0.2,  # Balanced creativity and control
            messages=[
                {
                    "role": "system",
                    "content": get_resume_optimization_prompt()
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        response_text = response.choices[0].message.content.strip()

        # Extract JSON from response
        try:
            # Try to find JSON in the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
            optimized_data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing optimization response: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            # Fallback to original context
            return _build_optimization_response_from_context(context, ["Could not parse optimization response"])

        # Build response
        return _build_optimization_response(optimized_data, context, issues)

    except Exception as e:
        logger.error(f"Error optimizing resume content: {e}")
        return _build_optimization_response_from_context(context, ["Optimization failed, returning original content"])


def _build_optimization_response(
    optimized_data: Dict[str, Any],
    original_context: Dict[str, Any],
    issues: List[ReviewIssue]
) -> ResumeOptimizationResponse:
    """Build optimization response from LLM output."""
    try:
        # Extract and validate skills
        skills_data = optimized_data.get("skills", {})
        skills = Skills(
            technical=skills_data.get("technical", []) or [],
            soft=skills_data.get("soft", []) or [],
            tools=skills_data.get("tools", []) or []
        )

        # Extract experience entries
        experience = []
        for exp in optimized_data.get("experience", []):
            try:
                entry = ExperienceEntry(
                    title=exp.get("title", ""),
                    company=exp.get("company", ""),
                    start_date=exp.get("start_date", ""),
                    end_date=exp.get("end_date"),
                    location=exp.get("location", ""),
                    bullets=exp.get("bullets", [])
                )
                experience.append(entry)
            except Exception as e:
                logger.warning(f"Skipping invalid experience entry: {e}")

        # Extract projects
        projects = []
        for proj in optimized_data.get("projects", []):
            try:
                entry = ProjectEntry(
                    title=proj.get("title", ""),
                    url=proj.get("url"),
                    description=proj.get("description", "")
                )
                projects.append(entry)
            except Exception as e:
                logger.warning(f"Skipping invalid project entry: {e}")

        # Determine improvements made
        improvements = []
        original_page_count = len(str(original_context).split("\n")) / 60  # Rough estimate
        if len(experience) < len(original_context.get("experience", [])):
            improvements.append(f"Reduced experience from {len(original_context.get('experience', []))} to {len(experience)} entries")
        if len(projects) < len(original_context.get("projects", [])):
            improvements.append(f"Reduced projects from {len(original_context.get('projects', []))} to {len(projects)} entries")
        if optimized_data.get("objective") != original_context.get("objective"):
            improvements.append("Improved objective statement for clarity and impact")

        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            improvements.append(f"Fixed {len(critical_issues)} critical issues")

        return ResumeOptimizationResponse(
            objective=optimized_data.get("objective", ""),
            skills=skills,
            experience=experience,
            projects=projects,
            optimization_notes="Resume optimized for 1-page fit and improved impact",
            improvements_made=improvements or ["Content refined"]
        )

    except Exception as e:
        logger.error(f"Error building optimization response: {e}")
        return _build_optimization_response_from_context(original_context, ["Optimization failed"])


def _build_optimization_response_from_context(
    context: Dict[str, Any],
    improvements: List[str]
) -> ResumeOptimizationResponse:
    """Fallback: build response from original context."""
    return ResumeOptimizationResponse(
        objective=context.get("objective", ""),
        skills=Skills(
            technical=context.get("skills", {}).get("technical", []),
            soft=context.get("skills", {}).get("soft", []),
            tools=context.get("skills", {}).get("tools", [])
        ),
        experience=[
            ExperienceEntry(**exp) for exp in context.get("experience", [])
            if all(k in exp for k in ["title", "company", "start_date", "location", "bullets"])
        ],
        projects=[
            ProjectEntry(**proj) for proj in context.get("projects", [])
            if all(k in proj for k in ["title", "description"])
        ],
        optimization_notes="Using original content (optimization unavailable)",
        improvements_made=improvements
    )
