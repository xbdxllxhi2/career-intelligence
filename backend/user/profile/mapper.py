from typing import List
from .entity import (
    UserProfile as UserProfileEntity,
    SkillCategory as SkillCategoryEntity,
    EducationEntry as EducationEntryEntity,
    ExperienceEntry as ExperienceEntryEntity,
    ProjectEntry as ProjectEntryEntity,
)
from .model import UserProfile as UserProfileModel
from .model import SkillCategory, EducationEntry, ExperienceEntry, ProjectEntry


class UserProfileMapper:
    @staticmethod
    def entity_to_model(entity: UserProfileEntity) -> UserProfileModel:
        return UserProfileModel(
            first_name=entity.first_name,
            last_name=entity.last_name,
            phone=entity.phone,
            email=entity.email,
            city=entity.city,
            country=entity.country,
            linkedin=entity.linkedin,
            github=entity.github,
            summary=entity.summary,
            languages=entity.languages or {},
            extra_curricular=entity.extra_curricular or [],
            education=[
                EducationEntry(
                    degree=e.degree,
                    school=e.school,
                    institution=e.institution,
                    year=e.year,
                    coursework=e.coursework,
                )
                for e in (entity.education or [])
            ],
            skills=[
                SkillCategory(category=s.category, skills=s.skills or [])
                for s in (entity.skills or [])
            ],
            experience=[
                ExperienceEntry(
                    title=exp.title,
                    company=exp.company,
                    period=exp.period,
                    location=exp.location,
                    tags=exp.tags or [],
                    bullets=exp.bullets or [],
                )
                for exp in (entity.experience or [])
            ],
            projects=[
                ProjectEntry(
                    name=p.name,
                    description=p.description,
                    url=p.url,
                    year=p.year,
                    tags=p.tags or [],
                    bullets=p.bullets or [],
                )
                for p in (entity.projects or [])
            ],
        )

    @staticmethod
    def model_to_entity(
        model: UserProfileModel, entity: UserProfileEntity = None
    ) -> UserProfileEntity:
        if entity is None:
            entity = UserProfileEntity()
        entity.id = 1
        entity.user_id = 1  # TODO change this to real user_id extracted from jwt
        entity.first_name = model.first_name
        entity.last_name = model.last_name
        entity.phone = model.phone
        entity.email = model.email
        entity.city = model.city
        entity.country = model.country
        entity.linkedin = model.linkedin
        entity.github = model.github
        entity.summary = model.summary
        entity.languages = model.languages or {}
        entity.extra_curricular = model.extra_curricular or []

        # Education
        entity.education = [
            EducationEntryEntity(
                degree=e.degree,
                school=e.school,
                institution=e.institution,
                year=e.year,
                coursework=e.coursework,
            )
            for e in (model.education or [])
        ]

        # Skills
        entity.skills = [
            SkillCategoryEntity(category=s.category, skills=s.skills or [])
            for s in (model.skills or [])
        ]

        # Experience
        entity.experience = [
            ExperienceEntryEntity(
                title=exp.title,
                company=exp.company,
                period=exp.period,
                location=exp.location,
                tags=exp.tags or [],
                bullets=exp.bullets or [],
            )
            for exp in (model.experience or [])
        ]

        # Projects
        entity.projects = [
            ProjectEntryEntity(
                name=p.name,
                description=p.description,
                url=p.url,
                year=p.year,
                tags=p.tags or [],
                bullets=p.bullets or [],
            )
            for p in (model.projects or [])
        ]

        return entity
