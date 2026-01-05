from sqlalchemy import create_engine
from core.config import get_settings
from sqlalchemy.orm import sessionmaker

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
