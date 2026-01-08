from database.entity import BaseEntity
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship

class UserApplicationEntity(BaseEntity):
    __tablename__ = "user_applications"
    __table_args__ = (UniqueConstraint("user_id", "job_offer_id", name="uq_user_job"), {"schema": "app"})

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    job_offer_id = Column(String, index=True, nullable=False)
    company = Column(String, nullable=False)
    company_logo_url= Column(String, nullable=True)
    job_offer_title = Column(String, nullable=False)
    job_offer_url = Column(String, nullable=False)
    job_offer_country=Column(String, nullable=True)
    job_offer_region=Column(String, nullable=True)
    job_offer_city=Column(String, nullable=True)
    resume_used_link=Column(String, nullable=True)
    applied_through = Column(String, nullable=True)
    status = Column(String, nullable=False, server_default="APPLIED")
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    application_experience = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

    history = relationship("UserApplicationHistoryEntity", back_populates="application", cascade="all, delete-orphan")


class UserApplicationHistoryEntity(BaseEntity):
    __tablename__ = "user_application_history"
    __table_args__ = {"schema": "app"}

    id = Column(Integer, primary_key=True, index=True)
    user_application_id = Column(Integer, ForeignKey("app.user_applications.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    application = relationship("UserApplicationEntity", back_populates="history")
