from pydantic import BaseModel
from typing import List, Optional


class ReviewIssue(BaseModel):
    issue_type: str  # "page_count", "date_conflict", "content_length", "missing_section", "skill_mismatch"
    severity: str  # "critical", "warning", "info"
    description: str
    location: Optional[str] = None  # e.g., "experience[0]", "objective"


class ResumeReviewResponse(BaseModel):
    is_valid: bool
    page_count: int
    issues: List[ReviewIssue] = []
    feedback: str
    recommendations: str
