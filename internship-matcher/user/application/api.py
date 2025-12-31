from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .models import CreateUserApplicationCommand
from . import service

router = APIRouter(prefix="/user/applications", tags=["user_applications"])


@router.post("", summary="Save a user application")
def save_user_application_api(request: CreateUserApplicationCommand):
    service.save_user_application(request)
    return JSONResponse(status_code=201, content={"message": "User application created successfully"})


@router.get("", summary="Get all user applications")
def get_user_applications_api():
    applications = service.get_user_applications()
    return applications


@router.delete("/{application_id}", summary="Delete a user application by ID")
def delete_user_application_api(application_id: int):
    service.delete_user_application(application_id)
    return JSONResponse(status_code=204)