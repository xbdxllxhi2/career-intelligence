from typing import Literal

from pydantic import BaseModel, Field


class DimensionScore(BaseModel):
    dimension: str = Field(
        description="One of: job_alignment, impact, clarity, ats_keywords, conciseness."
    )
    score: int = Field(description="Score from 1 (poor) to 5 (excellent).")
    comment: str = Field(description="Short justification for the score.")


class ReviewIssue(BaseModel):
    severity: Literal["critical", "major", "minor"]
    location: str = Field(
        description="Where the issue is, e.g. 'objective', 'experience[0].bullets[1]'."
    )
    issue: str = Field(description="What is wrong.")
    suggestion: str = Field(
        description="Concrete, actionable fix using only the candidate's real facts."
    )


class ResumeReviewVerdict(BaseModel):
    """Judge-only verdict produced by the reviewer agent.

    The reviewer never rewrites content; it only evaluates and suggests. The
    generator applies the feedback in a separate revise step.
    """

    passed: bool = Field(
        description="True if the resume is good enough to ship without further revision."
    )
    overall_score: int = Field(description="Overall quality from 1 to 10.")
    grounded: bool = Field(
        description="False if any claim, metric or technology is NOT supported by the profile."
    )
    dimensions: list[DimensionScore]
    issues: list[ReviewIssue]
    summary: str = Field(description="2-3 sentence overall assessment.")
