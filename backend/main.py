from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from jobs.api import router as jobs_router
from resume.resume_api import router as resume_router
from user.application.api import router as user_application_router
from user.profile.api import router as user_profile_router

from database.entity import BaseEntity
from database.engine import engine

import logging



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode="w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
logger = logging.getLogger("myapp")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database tables...")
    BaseEntity.metadata.create_all(engine)
    yield
    # Shutdown
    logger.info("Application shutdown...")
    
    
    
app = FastAPI(lifespan=lifespan, title="Internships Helper API", version="1.0.0")

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

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and load balancers"""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "Internships Helper API", "version": "1.0.0"}

app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(user_application_router)
app.include_router(user_profile_router)
