from typing import Any
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_keycloak_middleware import get_user

from .models import CreateUserApplicationCommand
from . import service

router = APIRouter(prefix="/user/applications", tags=["user_applications"])


@router.post("", summary="Save a user application")
def save_user_application_api(request: CreateUserApplicationCommand, user: Any = Depends(get_user)):
    user_id = user.user_id  # Keycloak user ID from token
    service.save_user_application(user_id, request)
    return JSONResponse(status_code=201, content={"message": "User application created successfully"})


@router.get("", summary="Get all user applications")
def get_user_applications_api(user: Any = Depends(get_user)):
    user_id = user.user_id  # Keycloak user ID from token
    applications = service.get_user_applications(user_id)
    return applications


@router.delete("/{application_id}", summary="Delete a user application by ID")
def delete_user_application_api(application_id: int, user: Any = Depends(get_user)):
    user_id = user.user_id  # Keycloak user ID from token
    service.delete_user_application(user_id, application_id)
    return JSONResponse(status_code=204, content={"message": "User application deleted successfully"})