"""
Job Matching Service - Uses LLM to analyze how well a user profile matches a job posting.
"""
import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from openai import OpenAI

from models.job_matching_response import JobMatchingResponse
from prompts.job_matching_prompts import get_job_matching_prompt, get_job_matching_user_prompt
from user.profile.model import UserProfile


logger = logging.getLogger(__name__)


# Initialize the Groq client with OpenAI-compatible API
groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY", ""),
)


class JobMatchingService:
    """Service for analyzing job-profile matching using LLM."""
    
    def __init__(self):
        self.client = groq_client
        self.model = "openai/gpt-oss-120b"  # Fast and capable model
    
    def analyze_match(
        self, 
        job_reference: str,
        job_description: str, 
        user_profile: UserProfile
    ) -> JobMatchingResponse:
        """
        Analyze how well a user profile matches a job posting.
        
        Args:
            job_reference: Unique identifier for the job
            job_description: Full job posting text
            user_profile: User's profile data
            
        Returns:
            JobMatchingResponse with detailed matching analysis
        """
        try:
            # Convert profile to readable format for LLM
            profile_text = self._format_profile(user_profile)
            
            # Build the prompt
            system_prompt = get_job_matching_prompt()
            user_prompt = get_job_matching_user_prompt(
                job_description=job_description,
                user_profile=profile_text,
                job_reference=job_reference
            )
            
            # Call LLM with structured output
            response = self.client.responses.parse(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                text_format=JobMatchingResponse,
                temperature=0.2,
                # max_tokens=8000,
            )
            
            result = response.output_parsed
            
            # Ensure calculated_at is set
            if not result.calculated_at:
                result.calculated_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Job matching completed for {job_reference}: overall_score={result.overall_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing job match for {job_reference}: {e}")
            # Return a fallback response on error
            return self._create_fallback_response(job_reference)
    
    def _format_profile(self, profile: UserProfile) -> str:
        """Format user profile into readable text for LLM analysis."""
        sections = []
        
        # Basic info
        if profile.first_name or profile.last_name:
            sections.append(f"Name: {profile.first_name or ''} {profile.last_name or ''}".strip())
        if profile.city or profile.country:
            location = ", ".join(filter(None, [profile.city, profile.country]))
            sections.append(f"Location: {location}")
        if profile.summary:
            sections.append(f"Summary: {profile.summary}")
        
        # Education
        if profile.education:
            edu_lines = ["Education:"]
            for edu in profile.education:
                institution = edu.institution or edu.school or "Unknown Institution"
                edu_lines.append(f"  - {edu.degree} at {institution} ({edu.year})")
                if edu.coursework:
                    edu_lines.append(f"    Coursework: {edu.coursework}")
            sections.append("\n".join(edu_lines))
        
        # Skills
        if profile.skills:
            skills_lines = ["Skills:"]
            for skill_cat in profile.skills:
                if skill_cat.skills:
                    skills_lines.append(f"  - {skill_cat.category}: {', '.join(skill_cat.skills)}")
            sections.append("\n".join(skills_lines))
        
        # Experience
        if profile.experience:
            exp_lines = ["Experience:"]
            for exp in profile.experience:
                company = exp.company or "Unknown Company"
                period = exp.period or "Unknown Period"
                exp_lines.append(f"  - {exp.title} at {company} ({period})")
                if exp.location:
                    exp_lines.append(f"    Location: {exp.location}")
                for bullet in exp.bullets[:3]:  # Limit bullets to avoid token overflow
                    exp_lines.append(f"    • {bullet}")
            sections.append("\n".join(exp_lines))
        
        # Projects
        if profile.projects:
            proj_lines = ["Projects:"]
            for proj in profile.projects:
                proj_lines.append(f"  - {proj.name}")
                if proj.description:
                    proj_lines.append(f"    {proj.description[:200]}...")  # Truncate long descriptions
                if proj.tags:
                    proj_lines.append(f"    Technologies: {', '.join(proj.tags)}")
            sections.append("\n".join(proj_lines))
        
        # Languages
        if profile.languages:
            lang_lines = ["Languages:"]
            for lang, level in profile.languages.items():
                lang_lines.append(f"  - {lang}: {level}")
            sections.append("\n".join(lang_lines))
        
        return "\n\n".join(sections)
    
    def _create_fallback_response(self, job_reference: str) -> JobMatchingResponse:
        """Create a fallback response when LLM analysis fails."""
        from models.job_matching_response import (
            MatchCategory, MatchCategoryType, MatchRecommendation,
            RecommendationActionType
        )
        
        return JobMatchingResponse(
            job_reference=job_reference,
            overall_score=0,
            match_categories=[
                MatchCategory(
                    category=MatchCategoryType.SKILLS,
                    score=0,
                    weight=0.30,
                    matched_items=[],
                    missing_items=[],
                    details="Unable to analyze - please try again"
                )
            ],
            recommendations=[
                MatchRecommendation(
                    category=MatchCategoryType.SKILLS,
                    title="Complete your profile",
                    description="Make sure your profile is complete for better matching",
                    impact="high",
                    action_type=RecommendationActionType.IMPROVE_PROFILE
                )
            ],
            calculated_at=datetime.now(timezone.utc).isoformat()
        )


# Singleton instance
job_matching_service = JobMatchingService()


def get_job_matching(
    job_reference: str,
    job_description: str,
    user_profile: UserProfile
) -> JobMatchingResponse:
    """
    Convenience function to get job matching analysis.
    
    Args:
        job_reference: Unique identifier for the job
        job_description: Full job posting text
        user_profile: User's profile data
        
    Returns:
        JobMatchingResponse with detailed matching analysis
    """
    return job_matching_service.analyze_match(
        job_reference=job_reference,
        job_description=job_description,
        user_profile=user_profile
    )
