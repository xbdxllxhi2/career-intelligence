from pydantic import BaseModel
from models.llm_resume_generation_response import Skills, ExperienceEntry, ProjectEntry
from typing import List


class ResumeOptimizationResponse(BaseModel):
    objective: str
    skills: Skills
    experience: list[ExperienceEntry]
    projects: list[ProjectEntry]
    optimization_notes: str
    improvements_made: List[str]
