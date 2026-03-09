from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_keycloak_middleware import KeycloakConfiguration, setup_keycloak_middleware
from fastapi_keycloak_middleware.fast_api_user import FastApiUser

from contextlib import asynccontextmanager
import os
from typing import Dict, Any

from flask.cli import load_dotenv

from jobs.api import router as jobs_router
from jobs.public_api import router as public_jobs_router
from resume.resume_api import router as resume_router
from user.application.api import router as user_application_router
from user.profile.api import router as user_profile_router

from database.entity import BaseEntity
from database.engine import engine

import logging

load_dotenv()
    

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode="w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
# logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger("myapp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database tables...")
    BaseEntity.metadata.create_all(engine)
    yield
    # Shutdown
    logger.info("Application shutdown...")
    
    
ENV = os.getenv("ENV", "dev").lower()
IS_PROD = ENV in ("prod", "production")


app = FastAPI(
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
    lifespan=lifespan, title="Internships Helper API", version="1.0.0"
)    

####################################################################
# Keycloak configuration
async def user_mapper(userinfo: Dict[str, Any]) -> FastApiUser:
    """Map Keycloak token claims to FastApiUser object."""
    return FastApiUser(
        first_name=userinfo.get("given_name", ""),
        last_name=userinfo.get("family_name", ""),
        user_id=userinfo.get("sub", "")  # sub is the Keycloak user ID
    )

keycloak_config = KeycloakConfiguration(
    url=os.getenv("KEYCLOAK_URL", "http://localhost:8080/auth/"),
    realm=os.getenv("KEYCLOAK_REALM", "myrealm"),
    client_id=os.getenv("KEYCLOAK_CLIENT_ID", "myclient"),
    client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET", None),
    verify=True,
    validate_token=True
)
setup_keycloak_middleware(
    app, 
    keycloak_config,
    user_mapper=user_mapper,
    exclude_patterns=[
        "/health",
        "/public/*"
    ]
)
#####################################################################

####################################################################
# Configure CORS from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins = [origin.strip() for origin in allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)
#####################################################################

#####################################################################
# Health check and root endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers"""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "Career Intelligence API", "version": "1.0.0"}

app.include_router(jobs_router)
app.include_router(public_jobs_router)
app.include_router(resume_router)
app.include_router(user_application_router)
app.include_router(user_profile_router)
