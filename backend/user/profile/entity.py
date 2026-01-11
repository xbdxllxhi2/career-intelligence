from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from typing import Optional

from database.entity import BaseEntity


class UserProfile(BaseEntity):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id= Column(Integer, index=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    email = Column(String(255))
    city = Column(String(100))
    country = Column(String(100))
    linkedin = Column(String(255))
    github = Column(String(255))
    summary = Column(Text)

    languages = Column(JSON, default=dict)
    extra_curricular = Column(JSON, default=list)

    education = relationship(
        "EducationEntry",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    skills = relationship(
        "SkillCategory",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    experience = relationship(
        "ExperienceEntry",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    projects = relationship(
        "ProjectEntry",
        back_populates="profile",
        cascade="all, delete-orphan",
    )


class SkillCategory(BaseEntity):
    __tablename__ = "user_profile_skill_categories"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    category = Column(String(100), nullable=False)
    skills = Column(JSON, default=list)

    profile = relationship("UserProfile", back_populates="skills")


class EducationEntry(BaseEntity):
    __tablename__ = "user_profile_education_entries"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    degree = Column(String(255), nullable=False)
    school = Column(String(255))
    institution = Column(String(255))
    year = Column(String(20), nullable=False)
    coursework = Column(Text)

    profile = relationship("UserProfile", back_populates="education")


class ExperienceEntry(BaseEntity):
    __tablename__ = "user_profile_experience_entries"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    title = Column(String(255), nullable=False)
    company = Column(String(255))
    period = Column(String(100))
    location = Column(String(100))

    tags = Column(JSON, default=list)
    bullets = Column(JSON, default=list)

    profile = relationship("UserProfile", back_populates="experience")


class ProjectEntry(BaseEntity):
    __tablename__ = "user_profile_project_entries"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description=Column(String(1024))
    url = Column(String(255))
    year = Column(String(20))

    tags = Column(JSON, default=list)
    bullets = Column(JSON, default=list)

    profile = relationship("UserProfile", back_populates="projects")
