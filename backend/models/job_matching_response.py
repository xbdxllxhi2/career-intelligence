from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


class MatchCategoryType(str, Enum):
    EDUCATION = "education"
    EXPERIENCE = "experience"
    SKILLS = "skills"
    LANGUAGES = "languages"
    CERTIFICATIONS = "certifications"
    LOCATION = "location"


class MatchStrength(str, Enum):
    EXACT = "exact"
    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"


class RequirementImportance(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    NICE_TO_HAVE = "nice-to-have"


class RecommendationActionType(str, Enum):
    ADD_SKILL = "add_skill"
    UPDATE_EXPERIENCE = "update_experience"
    ADD_CERTIFICATION = "add_certification"
    UPDATE_EDUCATION = "update_education"
    IMPROVE_PROFILE = "improve_profile"


class MatchedItem(BaseModel):
    """An item from the user profile that matches a job requirement"""
    user_value: str = Field(..., alias="userValue", description="What the user has")
    job_requirement: str = Field(..., alias="jobRequirement", description="What the job requires")
    match_strength: MatchStrength = Field(..., alias="matchStrength")
    details: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "by_alias": True,
    }


class MissingItem(BaseModel):
    """A job requirement that the user doesn't meet"""
    requirement: str = Field(..., description="What the job requires")
    importance: RequirementImportance
    suggestion: Optional[str] = Field(None, description="How the user could address this gap")

    model_config = {
        "populate_by_name": True,
        "by_alias": True,
    }


class MatchCategory(BaseModel):
    """Individual matching category (education, experience, skills, etc.)"""
    category: MatchCategoryType
    score: int = Field(..., ge=0, le=100, description="Match score for this category")
    weight: float = Field(..., ge=0, le=1, description="How much this category contributes to overall score")
    matched_items: List[MatchedItem] = Field(default_factory=list, alias="matchedItems")
    missing_items: List[MissingItem] = Field(default_factory=list, alias="missingItems")
    details: Optional[str] = Field(None, description="Additional context")

    model_config = {
        "populate_by_name": True,
        "by_alias": True,
    }


class MatchRecommendation(BaseModel):
    """Actionable recommendations to improve matching score"""
    category: MatchCategoryType
    title: str
    description: str
    impact: Literal["high", "medium", "low"]
    action_type: RecommendationActionType = Field(..., alias="actionType")

    model_config = {
        "populate_by_name": True,
        "by_alias": True,
    }


class JobMatchingResponse(BaseModel):
    """
    Job Matching Response - returned by the backend when comparing a user profile to a job offer.
    This model is used as response_model for LLM structured output.
    """
    job_reference: str = Field(..., alias="jobReference")
    overall_score: int = Field(..., ge=0, le=100, alias="overallScore", description="Aggregate match score")
    match_categories: List[MatchCategory] = Field(..., alias="matchCategories")
    recommendations: List[MatchRecommendation] = Field(default_factory=list)
    calculated_at: str = Field(..., alias="calculatedAt", description="ISO timestamp")

    model_config = {
        "populate_by_name": True,
        "by_alias": True,
    }
