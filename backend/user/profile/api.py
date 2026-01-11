import stat
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from database import engine

from .model import UserProfile
from .mapper import UserProfileMapper
from .service import UserProfileService

router = APIRouter(prefix="/user/profile", tags=["user_profile"])


@router.put("", summary="Update user profile")
def update_user_profile(
    profile_model: UserProfile, db: Session = Depends(engine.get_db)
) -> UserProfile:
    """
    Update a user profile. Expects full profile data.
    """
    service = UserProfileService(db)
    try:
        profile_entity = UserProfileMapper.model_to_entity(profile_model)
        updated_profile_entity = service.update_profile(
            user_id=1, entity=profile_entity
        )
        updated_profile_model = UserProfileMapper.entity_to_model(
            updated_profile_entity
        )
        return updated_profile_model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    
@router.get("",response_model=UserProfile)
def getUserProfile(db:Session= Depends(engine.get_db))-> UserProfile :
    service = UserProfileService(db)
    try:
        user_profile_entity = service.get_profile(1)
        user_profile_model = UserProfileMapper.entity_to_model(user_profile_entity)
        return user_profile_model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    
@router.post("",response_model=UserProfile)
def createUserProfile(profile:UserProfile,db:Session= Depends(engine.get_db))-> UserProfile :
    service = UserProfileService(db)
    try:
        entity_from_model = UserProfileMapper.model_to_entity(profile)
        user_profile_entity = service.create_profile(entity_from_model)
        user_profile_model = UserProfileMapper.entity_to_model(user_profile_entity)
        return user_profile_model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

