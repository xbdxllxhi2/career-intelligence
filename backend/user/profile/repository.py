from .entity import UserProfile as UserProfileEntity, EducationEntry, SkillCategory, ExperienceEntry, ProjectEntry
from sqlalchemy.orm import Session
from typing import Optional, List


class UserProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, entity: UserProfileEntity) -> UserProfileEntity:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, user_id: int) -> Optional[UserProfileEntity]:
        return self.session.query(UserProfileEntity).filter_by(id=user_id).first()

    def get_by_user_id(self, user_id: str) -> Optional[UserProfileEntity]:
        """Get profile by Keycloak user ID (sub claim)."""
        return self.session.query(UserProfileEntity).filter_by(user_id=user_id).first()

    def list_all(self) -> List[UserProfileEntity]:
        return self.session.query(UserProfileEntity).all()

 
    def update(self, user_id: str, entity: UserProfileEntity) -> Optional[UserProfileEntity]:
        existing = self.session.query(UserProfileEntity).filter_by(user_id=user_id).first()
        if not existing:
            return None

        # Copy scalar attributes from input entity to existing entity
        for attr in [
            "first_name", "last_name", "phone", "email", "city", "country",
            "linkedin", "github", "summary", "languages", "certifications", "extra_curricular"
        ]:
            setattr(existing, attr, getattr(entity, attr, None))

        # Clear existing relationships
        existing.education.clear()
        existing.skills.clear()
        existing.experience.clear()
        existing.projects.clear()

        # Create new relationship entries associated with existing profile
        for e in (entity.education or []):
            existing.education.append(EducationEntry(
                degree=e.degree, school=e.school, institution=e.institution,
                year=e.year, coursework=e.coursework
            ))
        
        for s in (entity.skills or []):
            existing.skills.append(SkillCategory(
                category=s.category, skills=s.skills
            ))
        
        for exp in (entity.experience or []):
            existing.experience.append(ExperienceEntry(
                title=exp.title, company=exp.company, period=exp.period,
                location=exp.location, tags=exp.tags, bullets=exp.bullets
            ))
        
        for p in (entity.projects or []):
            existing.projects.append(ProjectEntry(
                name=p.name, description=p.description, url=p.url,
                year=p.year, tags=p.tags, bullets=p.bullets
            ))

        self.session.commit()
        self.session.refresh(existing)
        return existing


    def createOrUpdate(self, user_id: str, entity: UserProfileEntity):
        print(f"DEBUG createOrUpdate: Looking for user_id='{user_id}'")
        existing = self.session.query(UserProfileEntity).filter_by(user_id=user_id).first()
        print(f"DEBUG createOrUpdate: Found existing={existing}")
        if not existing:
            print(f"DEBUG createOrUpdate: Creating new profile")
            return self.create(entity=entity)
        else:
            print(f"DEBUG createOrUpdate: Updating existing profile id={existing.id}")
            return self.update(user_id=user_id, entity=entity)
            

    def delete(self, user_id: str) -> bool:
        entity = self.session.query(UserProfileEntity).filter_by(user_id=user_id).first()
        if not entity:
            return False
        self.session.delete(entity)
        self.session.commit()
        return True
