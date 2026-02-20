/**
 * Job Matching Response - returned by the backend when comparing a user profile to a job offer
 */
export interface JobMatchingResponse {
  jobReference: string;
  overallScore: number; // 0-100 aggregate score
  matchCategories: MatchCategory[];
  recommendations: MatchRecommendation[];
  calculatedAt: string; // ISO timestamp
}

/**
 * Individual matching category (education, experience, skills, etc.)
 */
export interface MatchCategory {
  category: MatchCategoryType;
  score: number; // 0-100
  weight: number; // How much this category contributes to overall score (0-1)
  matchedItems: MatchedItem[];
  missingItems: MissingItem[];
  details?: string; // Additional context from the backend
}

export type MatchCategoryType = 
  | 'education'
  | 'experience'
  | 'skills'
  | 'languages'
  | 'certifications'
  | 'location';

/**
 * An item from the user profile that matches a job requirement
 */
export interface MatchedItem {
  userValue: string;      // What the user has (e.g., "Bachelor's in Computer Science")
  jobRequirement: string; // What the job requires (e.g., "BS in CS or related field")
  matchStrength: MatchStrength;
  details?: string;
}

export type MatchStrength = 'exact' | 'strong' | 'partial' | 'weak';

/**
 * A job requirement that the user doesn't meet
 */
export interface MissingItem {
  requirement: string;     // What the job requires
  importance: RequirementImportance;
  suggestion?: string;     // How the user could address this gap
}

export type RequirementImportance = 'required' | 'preferred' | 'nice-to-have';

/**
 * Actionable recommendations to improve matching score
 */
export interface MatchRecommendation {
  category: MatchCategoryType;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low'; // How much this would improve the score
  actionType: RecommendationActionType;
}

export type RecommendationActionType = 
  | 'add_skill'
  | 'update_experience'
  | 'add_certification'
  | 'update_education'
  | 'improve_profile';

/**
 * Summary statistics for display in the UI meter group
 */
export interface MatchingSummary {
  education: CategorySummary;
  experience: CategorySummary;
  skills: CategorySummary;
  languages: CategorySummary;
  overall: number;
}

export interface CategorySummary {
  score: number;
  matchedCount: number;
  totalRequired: number;
}
