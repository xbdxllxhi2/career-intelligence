import re
import unicodedata
from typing import Any

from models.llm_resume_generation_response import (
    ExperienceEntry,
    ProjectEntry,
    ResumeGenerationResponse,
    Skills,
)


class ResumeMapper:
    LATEX_SPECIAL_CHARS = {
        "\\": r"\textbackslash{}",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "&": r"\&",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    _LATEX_ESCAPE_RE = re.compile(r"([\\%$#&_{}~^])")
    UNICODE_SPACES = r"[\u00A0\u2000-\u200B\u202F\u205F\u3000]"
    ZERO_WIDTH = r"[\u200B\u200C\u200D\uFEFF]"

    @classmethod
    def normalize_text(cls, text: str | None) -> str:
        if text is None:
            return ""

        text = unicodedata.normalize("NFKC", text)
        text = re.sub(cls.UNICODE_SPACES, " ", text)
        text = re.sub(cls.ZERO_WIDTH, "", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def escape_latex(cls, text: str | None) -> str:
        normalized_text = cls.normalize_text(text)
        return cls._LATEX_ESCAPE_RE.sub(
            lambda match: cls.LATEX_SPECIAL_CHARS[match.group(1)],
            normalized_text,
        )

    @classmethod
    def latex_safe_resume(
        cls,
        resume: ResumeGenerationResponse,
    ) -> ResumeGenerationResponse:
        return ResumeGenerationResponse(
            objective=cls.escape_latex(resume.objective),
            skills=Skills(
                technical=[cls.escape_latex(skill) for skill in resume.skills.technical],
                soft=[cls.escape_latex(skill) for skill in resume.skills.soft],
                tools=[cls.escape_latex(skill) for skill in resume.skills.tools],
            ),
            experience=[
                ExperienceEntry(
                    title=cls.escape_latex(experience.title),
                    company=cls.escape_latex(experience.company),
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                    location=cls.escape_latex(experience.location),
                    bullets=[cls.escape_latex(bullet) for bullet in experience.bullets],
                )
                for experience in resume.experience
            ],
            projects=[
                ProjectEntry(
                    title=cls.escape_latex(project.title),
                    url=project.url,
                    description=cls.escape_latex(project.description),
                )
                for project in resume.projects
            ],
        )

    @classmethod
    def _compose_location(cls, profile_info: dict[str, Any]) -> str:
        if profile_info.get("location"):
            return str(profile_info["location"])

        city = profile_info.get("city")
        country = profile_info.get("country")
        return ", ".join([part for part in [city, country] if part])

    @classmethod
    def _compose_name(cls, profile_info: dict[str, Any]) -> str:
        first_name = cls.normalize_text(profile_info.get("first_name") or "")
        last_name = cls.normalize_text(profile_info.get("last_name") or "")
        full_name = f"{first_name} {last_name}".strip()
        return full_name or "Candidat"

    @classmethod
    def _build_dynamic_education(
        cls,
        profile: dict[str, Any],
        default_location: str,
    ) -> list[dict[str, str]]:
        dynamic_education = []
        for education_entry in profile.get("education", []):
            institution = education_entry.get("institution") or education_entry.get("school") or ""
            dynamic_education.append(
                {
                    "degree": cls.escape_latex(education_entry.get("degree") or ""),
                    "institution": cls.escape_latex(institution),
                    "location": cls.escape_latex(education_entry.get("location") or default_location),
                    "year": cls.escape_latex(education_entry.get("year") or ""),
                    "coursework": cls.escape_latex(education_entry.get("coursework") or ""),
                }
            )
        return dynamic_education

    @classmethod
    def _build_dynamic_languages(cls, profile: dict[str, Any]) -> list[dict[str, str]]:
        languages = profile.get("languages") or {}

        if isinstance(languages, dict):
            return [
                {
                    "name": cls.escape_latex(str(name)),
                    "level": cls.escape_latex(str(level)),
                }
                for name, level in languages.items()
            ]

        if isinstance(languages, list):
            return [{"name": cls.escape_latex(str(language)), "level": ""} for language in languages]

        return []

    @classmethod
    def _build_dynamic_certifications(cls, profile: dict[str, Any]) -> list[dict[str, str]]:
        certifications = []
        for certification in profile.get("certifications", []):
            certifications.append(
                {
                    "name": cls.escape_latex(certification.get("name") or ""),
                    "issuer": cls.escape_latex(certification.get("issuer") or ""),
                    "date": cls.escape_latex(certification.get("date") or ""),
                    "url": cls.normalize_text(certification.get("url") or ""),
                }
            )
        return certifications

    @classmethod
    def build_complete_cv_context(
        cls,
        profile: dict[str, Any],
        generated_resume_response: ResumeGenerationResponse,
    ) -> dict[str, Any]:
        profile_info = profile.get("profile") or {}
        location = cls._compose_location(profile_info)

        generated_resume_parts = generated_resume_response.model_dump()
        if not generated_resume_parts.get("objective"):
            generated_resume_parts["objective"] = cls.escape_latex(profile_info.get("summary") or "")

        complete_cv_context = {
            "name": cls.escape_latex(cls._compose_name(profile_info)),
            "phone": cls.escape_latex(profile_info.get("phone") or ""),
            "city": cls.escape_latex(location),
            "email": cls.escape_latex(profile_info.get("email") or ""),
            "email_href": cls.normalize_text(profile_info.get("email") or ""),
            "linkedin_href": cls.normalize_text(profile_info.get("linkedin") or ""),
            "github_href": cls.normalize_text(profile_info.get("github") or ""),
            "education": cls._build_dynamic_education(profile, location),
            "languages": cls._build_dynamic_languages(profile),
            "certifications": cls._build_dynamic_certifications(profile),
        }

        return {**complete_cv_context, **generated_resume_parts}
