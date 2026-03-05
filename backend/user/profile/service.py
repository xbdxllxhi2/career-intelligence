from .entity import UserProfile
from .repository import UserProfileRepository
from sqlalchemy.orm import Session


class UserProfileService:
    def __init__(self, session: Session):
        self.repo = UserProfileRepository(session)
        

    def update_profile(self, user_id: str, entity: UserProfile) -> UserProfile:
        updated_entity = self.repo.update(user_id, entity)
        if not updated_entity:
            raise ValueError(f"UserProfile for user {user_id} not found")
        
        return updated_entity
    

    def create_profile(self, entity: UserProfile) -> UserProfile:
        saved_entity = self.repo.create(entity)
        return saved_entity
    
    def createOrUpdate(self, user_id: str, entity: UserProfile) -> UserProfile:
        entity = self.repo.createOrUpdate(user_id=user_id, entity=entity)
        return entity
    

    def get_profile(self, user_id: str) -> UserProfile:
        entity = self.repo.get_by_user_id(user_id)
        if not entity:
            raise ValueError(f"Profile for user {user_id} not found")
        return entity
    

    def delete_profile(self, user_id: str) -> bool:
        return self.repo.delete(user_id)
