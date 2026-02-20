import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, delay } from 'rxjs';
import { environment } from '../environments/environments';
import { 
  JobMatchingResponse, 
  MatchCategory, 
  MatchCategoryType,
  MatchingSummary 
} from '../models/interface/job-matching';

@Injectable({
  providedIn: 'root',
})
export class JobMatchingService {
  private readonly apiUrl = environment.apiUrl + '/matching';

  constructor(private client: HttpClient) {}

  /**
   * Get matching analysis between user profile and a specific job
   * @param jobReference - The job reference ID
   * @returns Observable with matching response
   */
  getJobMatching(jobReference: string): Observable<JobMatchingResponse> {
    // TODO: Replace with actual API call when backend is ready
    // return this.client.get<JobMatchingResponse>(`${this.apiUrl}/job/${jobReference}`);
    
    // Mock implementation
    return of(this.generateMockMatchingResponse(jobReference)).pipe(delay(500));
  }

  /**
   * Convert JobMatchingResponse to the format needed by the meter group component
   */
  toMatchingSummaryStats(response: JobMatchingResponse): MatchingSummary {
    const findCategory = (type: MatchCategoryType): MatchCategory | undefined => 
      response.matchCategories.find(c => c.category === type);

    const toCategorySummary = (category: MatchCategory | undefined) => ({
      score: category?.score ?? 0,
      matchedCount: category?.matchedItems.length ?? 0,
      totalRequired: (category?.matchedItems.length ?? 0) + (category?.missingItems.length ?? 0)
    });

    return {
      education: toCategorySummary(findCategory('education')),
      experience: toCategorySummary(findCategory('experience')),
      skills: toCategorySummary(findCategory('skills')),
      languages: toCategorySummary(findCategory('languages')),
      overall: response.overallScore
    };
  }

  /**
   * Mock data generator - simulates backend response
   */
  private generateMockMatchingResponse(jobReference: string): JobMatchingResponse {
    return {
      jobReference,
      overallScore: 72,
      calculatedAt: new Date().toISOString(),
      matchCategories: [
        {
          category: 'education',
          score: 85,
          weight: 0.2,
          matchedItems: [
            {
              userValue: "Bachelor's in Computer Science",
              jobRequirement: "BS in Computer Science or related field",
              matchStrength: 'exact',
              details: "Degree matches job requirement"
            }
          ],
          missingItems: [
            {
              requirement: "Master's degree preferred",
              importance: 'preferred',
              suggestion: "Consider pursuing a Master's degree to strengthen your profile"
            }
          ],
          details: "Your education background is a strong match for this position"
        },
        {
          category: 'experience',
          score: 65,
          weight: 0.3,
          matchedItems: [
            {
              userValue: "2 years as Software Developer at TechCorp",
              jobRequirement: "3+ years of software development experience",
              matchStrength: 'partial',
              details: "Close to required experience level"
            },
            {
              userValue: "Led team of 3 developers",
              jobRequirement: "Team collaboration experience",
              matchStrength: 'strong'
            }
          ],
          missingItems: [
            {
              requirement: "Experience with enterprise-scale applications",
              importance: 'required',
              suggestion: "Highlight any large-scale projects you've worked on"
            }
          ],
          details: "Your experience is relevant but slightly below the required years"
        },
        {
          category: 'skills',
          score: 78,
          weight: 0.35,
          matchedItems: [
            {
              userValue: "Python",
              jobRequirement: "Python proficiency",
              matchStrength: 'exact'
            },
            {
              userValue: "JavaScript, TypeScript",
              jobRequirement: "JavaScript/TypeScript",
              matchStrength: 'exact'
            },
            {
              userValue: "PostgreSQL",
              jobRequirement: "SQL databases",
              matchStrength: 'strong'
            },
            {
              userValue: "Docker",
              jobRequirement: "Containerization",
              matchStrength: 'exact'
            }
          ],
          missingItems: [
            {
              requirement: "Kubernetes",
              importance: 'required',
              suggestion: "Add Kubernetes to your skillset - consider online courses or certifications"
            },
            {
              requirement: "AWS or GCP cloud experience",
              importance: 'preferred',
              suggestion: "Gain cloud platform experience through projects or certifications"
            }
          ],
          details: "Good technical skills match with some gaps in cloud/DevOps"
        },
        {
          category: 'languages',
          score: 100,
          weight: 0.1,
          matchedItems: [
            {
              userValue: "English - Fluent",
              jobRequirement: "English proficiency",
              matchStrength: 'exact'
            }
          ],
          missingItems: [],
          details: "Language requirements fully met"
        },
        {
          category: 'location',
          score: 50,
          weight: 0.05,
          matchedItems: [],
          missingItems: [
            {
              requirement: "On-site in Paris preferred",
              importance: 'preferred',
              suggestion: "Position allows remote work but on-site candidates preferred"
            }
          ],
          details: "Remote work available but relocation could improve your chances"
        }
      ],
      recommendations: [
        {
          category: 'skills',
          title: "Learn Kubernetes",
          description: "This is a required skill for the position. Consider taking a certification course.",
          impact: 'high',
          actionType: 'add_skill'
        },
        {
          category: 'experience',
          title: "Highlight large projects",
          description: "Update your profile to emphasize any enterprise-scale work you've done.",
          impact: 'medium',
          actionType: 'update_experience'
        },
        {
          category: 'skills',
          title: "Get cloud certification",
          description: "AWS or GCP certification would strengthen your profile significantly.",
          impact: 'medium',
          actionType: 'add_certification'
        }
      ]
    };
  }
}
