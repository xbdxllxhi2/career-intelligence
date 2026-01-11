from .entity import UserProfile
from .repository import UserProfileRepository
from sqlalchemy.orm import Session


class UserProfileService:
    def __init__(self, session: Session):
        self.repo = UserProfileRepository(session)
        

    def update_profile(self, user_id, entity: UserProfile) -> UserProfile:
        updated_entity = self.repo.update(entity.id, entity)
        if not updated_entity:
            raise ValueError(f"UserProfile with id {entity.id} not found")
        
        return updated_entity
    

    def create_profile(self, entity: UserProfile) -> UserProfile:
        saved_entity = self.repo.create(entity)
        return saved_entity
    

    def get_profile(self, user_id: int) -> UserProfile:
        entity = self.repo.get_by_id(user_id)
        if not entity:
            raise ValueError(f"Profile with id {user_id} not found")
        return entity
    

    def delete_profile(self, user_id: int) -> bool:
        return self.repo.delete(user_id)
