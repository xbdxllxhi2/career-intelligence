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
    description: str
    # technologies: list[str]
    # link: str | None = None


class ResumeGenerationResponse(BaseModel):
    skills: Skills
    experience: list[ExperienceEntry]
    projects: list[ProjectEntry]
