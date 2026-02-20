import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JobMatchingStats } from './job-matching-stats';
import { TranslocoTestingModule } from '@jsverse/transloco';
import { JobMatchingResponse } from '../../models/interface/job-matching';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('JobMatchingStats', () => {
  let component: JobMatchingStats;
  let fixture: ComponentFixture<JobMatchingStats>;

  const mockMatchingResponse: JobMatchingResponse = {
    jobReference: 'test-job-123',
    overallScore: 75,
    calculatedAt: new Date().toISOString(),
    matchCategories: [
      {
        category: 'skills',
        score: 80,
        weight: 0.35,
        matchedItems: [
          { userValue: 'Python', jobRequirement: 'Python proficiency', matchStrength: 'exact' }
        ],
        missingItems: [
          { requirement: 'Kubernetes', importance: 'required', suggestion: 'Learn Kubernetes' }
        ]
      },
      {
        category: 'experience',
        score: 65,
        weight: 0.3,
        matchedItems: [
          { userValue: '2 years development', jobRequirement: '3+ years', matchStrength: 'partial' }
        ],
        missingItems: []
      },
      {
        category: 'education',
        score: 85,
        weight: 0.2,
        matchedItems: [
          { userValue: "Bachelor's CS", jobRequirement: 'BS in CS', matchStrength: 'exact' }
        ],
        missingItems: []
      }
    ],
    recommendations: [
      {
        category: 'skills',
        title: 'Learn Kubernetes',
        description: 'This is a required skill',
        impact: 'high',
        actionType: 'add_skill'
      }
    ]
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        JobMatchingStats,
        NoopAnimationsModule,
        TranslocoTestingModule.forRoot({
          langs: { en: {} },
          translocoConfig: { availableLangs: ['en'], defaultLang: 'en' }
        })
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(JobMatchingStats);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should emit updateProfileClick when button is clicked', () => {
    const spy = spyOn(component.updateProfileClick, 'emit');
    component.onUpdateProfileClick();
    expect(spy).toHaveBeenCalled();
  });

  it('should emit viewDetailsClick and open dialog when category is clicked', () => {
    component.matchingResponse = mockMatchingResponse;
    component.ngOnChanges({
      matchingResponse: {
        currentValue: mockMatchingResponse,
        previousValue: null,
        firstChange: true,
        isFirstChange: () => true
      }
    });
    
    const spy = spyOn(component.viewDetailsClick, 'emit');
    component.openCategoryDetails('skills');
    
    expect(spy).toHaveBeenCalledWith('skills');
    expect(component.showDetailsDialog).toBe(true);
    expect(component.selectedCategory?.category).toBe('skills');
  });

  it('should emit recommendationClick when recommendation is clicked', () => {
    const spy = spyOn(component.recommendationClick, 'emit');
    const recommendation = mockMatchingResponse.recommendations[0];
    component.onRecommendationClick(recommendation);
    expect(spy).toHaveBeenCalledWith(recommendation);
  });

  it('should process matching response and create stats', () => {
    component.matchingResponse = mockMatchingResponse;
    component.ngOnChanges({
      matchingResponse: {
        currentValue: mockMatchingResponse,
        previousValue: null,
        firstChange: true,
        isFirstChange: () => true
      }
    });
    fixture.detectChanges();
    
    expect(component.stats.length).toBe(3);
    expect(component.overallScore).toBe(75);
    expect(component.recommendations.length).toBe(1);
  });

  it('should build radar chart data from response', () => {
    component.matchingResponse = mockMatchingResponse;
    component.ngOnChanges({
      matchingResponse: {
        currentValue: mockMatchingResponse,
        previousValue: null,
        firstChange: true,
        isFirstChange: () => true
      }
    });
    fixture.detectChanges();
    
    expect(component.radarData).toBeTruthy();
    expect(component.radarData.datasets.length).toBe(2);
    expect(component.radarOptions).toBeTruthy();
  });

  it('should return correct score class', () => {
    expect(component.getScoreClass(85)).toBe('text-green-400');
    expect(component.getScoreClass(70)).toBe('text-yellow-400');
    expect(component.getScoreClass(50)).toBe('text-orange-400');
    expect(component.getScoreClass(30)).toBe('text-red-400');
  });

  it('should return correct score background class', () => {
    expect(component.getScoreBgClass(85)).toBe('bg-green-500/20');
    expect(component.getScoreBgClass(70)).toBe('bg-yellow-500/20');
    expect(component.getScoreBgClass(50)).toBe('bg-orange-500/20');
    expect(component.getScoreBgClass(30)).toBe('bg-red-500/20');
  });

  it('should return correct match strength class', () => {
    expect(component.getMatchStrengthClass('exact')).toBe('text-green-400 bg-green-500/20');
    expect(component.getMatchStrengthClass('strong')).toBe('text-emerald-400 bg-emerald-500/20');
    expect(component.getMatchStrengthClass('partial')).toBe('text-yellow-400 bg-yellow-500/20');
    expect(component.getMatchStrengthClass('weak')).toBe('text-orange-400 bg-orange-500/20');
  });

  it('should return correct importance class', () => {
    expect(component.getImportanceClass('required')).toBe('text-red-400 bg-red-500/20');
    expect(component.getImportanceClass('preferred')).toBe('text-yellow-400 bg-yellow-500/20');
    expect(component.getImportanceClass('nice-to-have')).toBe('text-blue-400 bg-blue-500/20');
  });

  it('should return correct impact severity', () => {
    expect(component.getImpactSeverity('high')).toBe('danger');
    expect(component.getImpactSeverity('medium')).toBe('warn');
    expect(component.getImpactSeverity('low')).toBe('info');
    expect(component.getImpactSeverity('unknown')).toBe('secondary');
  });

  it('should toggle view mode between meter and radar', () => {
    expect(component.viewMode).toBe('meter');
    component.viewMode = 'radar';
    expect(component.viewMode).toBe('radar');
  });

  it('should close details dialog', () => {
    component.showDetailsDialog = true;
    component.selectedCategory = mockMatchingResponse.matchCategories[0];
    
    component.closeDetailsDialog();
    
    expect(component.showDetailsDialog).toBe(false);
    expect(component.selectedCategory).toBeNull();
  });
});
