from typing import Literal, Optional

from pydantic import BaseModel, Field


class SkillCategory(BaseModel):
    """A labelled group of skills, e.g. 'Machine Learning & Generative AI'."""

    category: str = Field(description="Short category label, 2-4 words.")
    items: list[str] = Field(description="Skill keywords belonging to this category.")


class AgentExperienceEntry(BaseModel):
    title: str
    company: str
    start_date: str = Field(description="Human readable, e.g. 'Mar 2026'.")
    end_date: Optional[str] = Field(
        default=None, description="Human readable or 'Present'/'Présent' if ongoing."
    )
    location: Optional[str] = None
    context: Optional[str] = Field(
        default=None,
        description="One short line describing the company/mission scope, shown in italics.",
    )
    bullets: list[str]


class AgentProjectEntry(BaseModel):
    title: str
    subtitle: Optional[str] = Field(
        default=None, description="Optional tech-stack tagline, e.g. 'FastAPI/Angular'."
    )
    url: Optional[str] = None
    year: Optional[str] = None
    bullets: list[str]


class AgentResumeResponse(BaseModel):
    """Structured resume content produced by the generation agent.

    Education, languages and certifications are taken from the user profile and
    are intentionally not generated here.
    """

    language: Literal["en", "fr"] = Field(
        description="Language of the generated content, matching the job offer."
    )
    objective: str
    skills: list[SkillCategory]
    experience: list[AgentExperienceEntry]
    projects: list[AgentProjectEntry]
