from typing import Generator
from sqlalchemy import create_engine
from core.config import get_settings
from sqlalchemy.orm import sessionmaker, Session

settings = get_settings()


engine = create_engine(
    settings.ADMIN_DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for FastAPI requests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
