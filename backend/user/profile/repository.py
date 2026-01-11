from .entity import UserProfile as UserProfileEntity
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


    def list_all(self) -> List[UserProfileEntity]:
        return self.session.query(UserProfileEntity).all()

 
    def update(self, user_id: int, entity: UserProfileEntity) -> Optional[UserProfileEntity]:
        existing = self.session.query(UserProfileEntity).filter_by(id=user_id).first()
        if not existing:
            return None

        # Copy all attributes from input entity to existing entity
        # (excluding id and relationships if you want to manage them separately)
        for attr in [
            "first_name", "last_name", "phone", "email", "city", "country",
            "linkedin", "github", "summary", "languages", "extra_curricular"
        ]:
            setattr(existing, attr, getattr(entity, attr))

        # Optional: handle relationships like experience, skills, etc.
        existing.education = entity.education
        existing.skills = entity.skills
        existing.experience = entity.experience
        existing.projects = entity.projects

        self.session.commit()
        self.session.refresh(existing)
        return existing


    def delete(self, user_id: int) -> bool:
        entity = self.session.query(UserProfileEntity).filter_by(id=user_id).first()
        if not entity:
            return False
        self.session.delete(entity)
        self.session.commit()
        return True
