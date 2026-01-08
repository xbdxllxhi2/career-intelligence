from pydantic import BaseModel


class Skills(BaseModel):
    technical: list[str]
    soft: list[str]
    tools: list[str]
    
        
class ExperienceEntry(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: str | None = None
    location: str
    bullets: list[str]
    

class ProjectEntry(BaseModel):    
    title: str
    url: str | None = None
    description: str
    # technologies: list[str]


class ResumeGenerationResponse(BaseModel):
    objective: str
    skills: Skills
    experience: list[ExperienceEntry]
    projects: list[ProjectEntry]
