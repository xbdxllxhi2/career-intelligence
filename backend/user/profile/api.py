import stat
from typing import Any
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi_keycloak_middleware import get_user

from database import engine

from .model import UserProfile
from .mapper import UserProfileMapper
from .service import UserProfileService
from .resume_parser import ResumeParserService, ParsedProfile

router = APIRouter(prefix="/user/profile", tags=["user_profile"])


@router.put("", summary="Update user profile")
def update_user_profile(
    profile_model: UserProfile,
    user: Any = Depends(get_user),
    db: Session = Depends(engine.get_db)
) -> UserProfile:
    """
    Update a user profile. Expects full profile data.
    """
    user_id = user.user_id  # Keycloak user ID from token
    service = UserProfileService(db)
    try:
        profile_entity = UserProfileMapper.model_to_entity(profile_model)
        updated_profile_entity = service.update_profile(
            user_id=user_id, entity=profile_entity
        )
        updated_profile_model = UserProfileMapper.entity_to_model(
            updated_profile_entity
        )
        return updated_profile_model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    
@router.get("",response_model=UserProfile)
def getUserProfile(user: Any = Depends(get_user), db:Session= Depends(engine.get_db))-> UserProfile :
    user_id = user.user_id  # Keycloak user ID from token
    print(f"Fetching profile for user: {user_id}")
    service = UserProfileService(db)
    try:
        user_profile_entity = service.get_profile(user_id)
        user_profile_model = UserProfileMapper.entity_to_model(user_profile_entity)
        return user_profile_model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    
@router.post("",response_model=UserProfile)
def createUserProfile(profile:UserProfile, user: Any = Depends(get_user), db:Session= Depends(engine.get_db))-> UserProfile :
    user_id = user.user_id  # Keycloak user ID from token
    service = UserProfileService(db)
    try:
        entity_from_model = UserProfileMapper.model_to_entity(profile)
        entity_from_model.user_id = user_id  # Associate with authenticated user
        user_profile_entity = service.create_profile(entity_from_model)
        user_profile_model = UserProfileMapper.entity_to_model(user_profile_entity)
        return user_profile_model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/parse-resume", response_model=ParsedProfile, summary="Parse resume and extract profile data")
async def parse_resume(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX)")
) -> ParsedProfile:
    """
    Upload a resume file (PDF or DOCX) and extract profile data using AI.
    Returns structured profile data that can be used to populate the user profile.
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.docx']
    file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    try:
        parser = ResumeParserService()
        parsed_profile = parser.parse_resume(content, file.filename)
        return parsed_profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

