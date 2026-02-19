from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class SkillCategory(BaseModel):
    category: str = Field(..., description="Skill category name, e.g. Programming Languages")
    skills: List[str] = Field(default_factory=list)

class EducationEntry(BaseModel):
    degree: str
    school: Optional[str] = None
    institution: Optional[str] = None
    year: str
    coursework: Optional[str] = None

class ExperienceEntry(BaseModel):
    title: str
    company: Optional[str] = None
    period: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)

class ProjectEntry(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    year: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)

class UserProfile(BaseModel):
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None

    education: List[EducationEntry] = Field(default_factory=list)
    skills: List[SkillCategory] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    languages: Dict[str, str] = Field(default_factory=dict)
    extra_curricular: List[str] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
