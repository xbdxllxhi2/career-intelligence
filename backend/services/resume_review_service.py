import fitz  # PyMuPDF
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.resume_review_response import ReviewIssue, ResumeReviewResponse
from services.llm_writer import groq_open_ai_client
from prompts.prompts_bank import get_resume_review_prompt

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    try:
        pdf_document = fitz.open(pdf_path)
        text = ""
        for page in pdf_document:
            text += page.get_text() + "\n"
        pdf_document.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
        raise


def count_pdf_pages(pdf_path: str) -> int:
    """Count the number of pages in a PDF file."""
    try:
        pdf_document = fitz.open(pdf_path)
        page_count = len(pdf_document)
        pdf_document.close()
        return page_count
    except Exception as e:
        logger.error(f"Error counting pages in PDF {pdf_path}: {e}")
        raise


def _parse_dates(date_str: str) -> Optional[datetime]:
    """Parse various date formats into datetime objects."""
    if not date_str or date_str.lower() in ["present", "current", "now"]:
        return None

    formats = ["%Y-%m-%d", "%m/%d/%Y", "%Y", "%B %Y", "%b %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _validate_dates(experience: List[Dict[str, Any]]) -> List[ReviewIssue]:
    """Check for date conflicts in experience (overlaps or wrong order)."""
    issues = []

    # Sort by start date to check for overlaps
    sorted_exp = sorted(
        [(i, exp) for i, exp in enumerate(experience)],
        key=lambda x: _parse_dates(x[1].get("start_date", "")) or datetime.min,
        reverse=True  # Most recent first
    )

    for i in range(len(sorted_exp) - 1):
        current_idx, current = sorted_exp[i]
        next_idx, next_exp = sorted_exp[i + 1]

        current_start = _parse_dates(current.get("start_date", ""))
        current_end = _parse_dates(current.get("end_date", ""))
        next_start = _parse_dates(next_exp.get("start_date", ""))
        next_end = _parse_dates(next_exp.get("end_date", ""))

        # Check for overlaps
        if current_start and next_end and current_start < next_end:
            issues.append(ReviewIssue(
                issue_type="date_conflict",
                severity="warning",
                description=f"Potential date overlap: {next_exp.get('company', 'Unknown')} ({next_exp.get('start_date', 'Unknown')} - {next_exp.get('end_date', 'Unknown')}) overlaps with {current.get('company', 'Unknown')}",
                location=f"experience[{current_idx}]"
            ))

    return issues


def _validate_content_lengths(context: Dict[str, Any]) -> List[ReviewIssue]:
    """Check for content length violations."""
    issues = []

    # Objective validation: 14-22 words, single sentence
    objective = context.get("objective", "").strip()
    if objective:
        word_count = len(objective.split())
        if word_count < 14 or word_count > 22:
            issues.append(ReviewIssue(
                issue_type="content_length",
                severity="warning",
                description=f"Objective has {word_count} words (should be 14-22 words)",
                location="objective"
            ))

    # Experience bullets: 70-100 chars each
    experience = context.get("experience", [])
    for exp_idx, exp in enumerate(experience):
        for bullet_idx, bullet in enumerate(exp.get("bullets", [])):
            bullet_len = len(bullet)
            if bullet_len < 70 or bullet_len > 100:
                issues.append(ReviewIssue(
                    issue_type="content_length",
                    severity="info",
                    description=f"Bullet has {bullet_len} chars (ideal: 70-100)",
                    location=f"experience[{exp_idx}].bullets[{bullet_idx}]"
                ))

    return issues


def _validate_missing_sections(context: Dict[str, Any]) -> List[ReviewIssue]:
    """Check for missing critical sections."""
    issues = []

    # Objective is required
    if not context.get("objective", "").strip():
        issues.append(ReviewIssue(
            issue_type="missing_section",
            severity="critical",
            description="Objective is missing",
            location="objective"
        ))

    # At least one experience entry required
    experience = context.get("experience", [])
    if not experience or len(experience) == 0:
        issues.append(ReviewIssue(
            issue_type="missing_section",
            severity="critical",
            description="No experience entries found",
            location="experience"
        ))

    # Skills with at least one skill required
    skills = context.get("skills", {})
    total_skills = len(skills.get("technical", [])) + len(skills.get("soft", [])) + len(skills.get("tools", []))
    if total_skills == 0:
        issues.append(ReviewIssue(
            issue_type="missing_section",
            severity="critical",
            description="No skills found",
            location="skills"
        ))

    return issues


def _validate_skill_experience_match(context: Dict[str, Any]) -> List[ReviewIssue]:
    """Check for skills mentioned in experience/projects."""
    issues = []

    # Extract all skills
    skills = context.get("skills", {})
    all_skills = set(
        skills.get("technical", []) +
        skills.get("soft", []) +
        skills.get("tools", [])
    )

    # Extract all text from experience and projects
    experience_text = ""
    for exp in context.get("experience", []):
        experience_text += " ".join(exp.get("bullets", [])) + " "

    projects_text = ""
    for proj in context.get("projects", []):
        projects_text += proj.get("description", "") + " "

    content_text = (experience_text + projects_text).lower()

    # Check if skills appear in experience/projects
    unused_skills = []
    for skill in all_skills:
        if skill.lower() not in content_text:
            unused_skills.append(skill)

    if unused_skills:
        issues.append(ReviewIssue(
            issue_type="skill_mismatch",
            severity="warning",
            description=f"Skills not mentioned in experience/projects: {', '.join(unused_skills[:3])}",
            location="skills"
        ))

    return issues


def validate_resume_structure(context: Dict[str, Any]) -> List[ReviewIssue]:
    """Validate resume structure for all inconsistencies."""
    issues = []

    # Check for date conflicts
    issues.extend(_validate_dates(context.get("experience", [])))

    # Check for content length violations
    issues.extend(_validate_content_lengths(context))

    # Check for missing critical sections
    issues.extend(_validate_missing_sections(context))

    # Check for skill-experience mismatches
    issues.extend(_validate_skill_experience_match(context))

    return issues


def analyze_resume_with_llm(pdf_text: str, context: Dict[str, Any]) -> ResumeReviewResponse:
    """Analyze resume with LLM to identify quality issues and provide feedback."""
    try:
        page_count = len(pdf_text.split("\n\f"))  # Form feed is page separator

        # Run structural validation
        structural_issues = validate_resume_structure(context)

        # Call LLM for quality analysis
        response = groq_open_ai_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0.1,  # Deterministic analysis
            messages=[
                {
                    "role": "system",
                    "content": get_resume_review_prompt()
                },
                {
                    "role": "user",
                    "content": f"""Resume Content:
{pdf_text[:2000]}

Please analyze this resume and provide:
1. A brief assessment (2-3 sentences)
2. Specific recommendations for improvement (3-5 bullet points)"""
                }
            ]
        )

        llm_feedback = response.choices[0].message.content.strip()

        # Determine if resume is valid
        critical_issues = [i for i in structural_issues if i.severity == "critical"]
        is_valid = len(critical_issues) == 0 and page_count <= 1

        return ResumeReviewResponse(
            is_valid=is_valid,
            page_count=page_count,
            issues=structural_issues,
            feedback=llm_feedback,
            recommendations="Review structural issues and follow LLM recommendations"
        )

    except Exception as e:
        logger.error(f"Error analyzing resume with LLM: {e}")
        # Return fallback response with structural issues only
        page_count = len(pdf_text.split("\n\f"))
        structural_issues = validate_resume_structure(context)
        critical_issues = [i for i in structural_issues if i.severity == "critical"]

        return ResumeReviewResponse(
            is_valid=len(critical_issues) == 0 and page_count <= 1,
            page_count=page_count,
            issues=structural_issues,
            feedback="Resume quality analysis unavailable",
            recommendations="Please review structural issues detected"
        )
