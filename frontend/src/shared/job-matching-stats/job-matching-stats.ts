import { Component, EventEmitter, Input, Output, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PanelModule } from 'primeng/panel';
import { MeterGroupModule } from 'primeng/metergroup';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TranslocoModule } from '@jsverse/transloco';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { TooltipModule } from 'primeng/tooltip';
import { TagModule } from 'primeng/tag';
import { DialogModule } from 'primeng/dialog';
import { ChartModule } from 'primeng/chart';
import { SelectButtonModule } from 'primeng/selectbutton';
import { FormsModule } from '@angular/forms';
import { DividerModule } from 'primeng/divider';
import { 
  JobMatchingResponse, 
  MatchCategory, 
  MatchRecommendation,
  MatchCategoryType,
  MatchedItem,
  MissingItem
} from '../../models/interface/job-matching';

export interface MatchingStatItem {
  label: string;
  translationKey: string;
  color1: string;
  color2: string;
  value: number;
  icon: string;
  category: MatchCategoryType;
  matchedCount?: number;
  totalCount?: number;
}

export type ViewMode = 'meter' | 'radar';

@Component({
  selector: 'app-job-matching-stats',
  standalone: true,
  imports: [
    CommonModule,
    PanelModule,
    MeterGroupModule,
    CardModule,
    ButtonModule,
    TranslocoModule,
    ProgressSpinnerModule,
    TooltipModule,
    TagModule,
    DialogModule,
    ChartModule,
    SelectButtonModule,
    FormsModule,
    DividerModule
  ],
  templateUrl: './job-matching-stats.html',
  styleUrl: './job-matching-stats.scss'
})
export class JobMatchingStats implements OnChanges {
  @Input() matchingResponse: JobMatchingResponse | null = null;
  @Input() loading: boolean = false;
  @Input() collapsed: boolean = true;
  @Input() showUpdateProfileButton: boolean = true;
  @Input() showRecommendations: boolean = true;
  @Input() showRadarOption: boolean = true;
  @Input() panelHeader: string = 'jobs.skillsMatch';
  
  @Output() updateProfileClick = new EventEmitter<void>();
  @Output() viewDetailsClick = new EventEmitter<MatchCategoryType>();
  @Output() recommendationClick = new EventEmitter<MatchRecommendation>();

  stats: MatchingStatItem[] = [];
  recommendations: MatchRecommendation[] = [];
  overallScore: number = 0;

  // View mode toggle
  viewMode: ViewMode = 'meter';
  viewModeOptions = [
    { label: 'Meter', value: 'meter', icon: 'pi pi-chart-bar' },
    { label: 'Radar', value: 'radar', icon: 'pi pi-chart-pie' }
  ];

  // Radar chart data
  radarData: any = null;
  radarOptions: any = null;

  // Category details dialog
  showDetailsDialog: boolean = false;
  selectedCategory: MatchCategory | null = null;
  selectedCategoryConfig: { icon: string; color1: string; color2: string; translationKey: string } | null = null;

  private categoryConfig: Record<MatchCategoryType, { icon: string; color1: string; color2: string; translationKey: string }> = {
    education: { icon: 'pi pi-graduation-cap', color1: '#3b82f6', color2: '#60a5fa', translationKey: 'matching.education' },
    experience: { icon: 'pi pi-briefcase', color1: '#8b5cf6', color2: '#a78bfa', translationKey: 'matching.experience' },
    skills: { icon: 'pi pi-code', color1: '#10b981', color2: '#34d399', translationKey: 'matching.skills' },
    languages: { icon: 'pi pi-globe', color1: '#f59e0b', color2: '#fbbf24', translationKey: 'matching.languages' },
    certifications: { icon: 'pi pi-verified', color1: '#ec4899', color2: '#f472b6', translationKey: 'matching.certifications' },
    location: { icon: 'pi pi-map-marker', color1: '#6366f1', color2: '#818cf8', translationKey: 'matching.location' }
  };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['matchingResponse'] && this.matchingResponse) {
      this.processMatchingResponse(this.matchingResponse);
    }
  }

  private processMatchingResponse(response: JobMatchingResponse): void {
    this.overallScore = response.overallScore;
    this.recommendations = response.recommendations;
    
    this.stats = response.matchCategories
      .filter(cat => cat.weight > 0)
      .map(category => this.categoryToStatItem(category));

    this.buildRadarChart(response);
  }

  private categoryToStatItem(category: MatchCategory): MatchingStatItem {
    const config = this.categoryConfig[category.category];
    return {
      label: category.category,
      translationKey: config.translationKey,
      color1: config.color1,
      color2: config.color2,
      value: category.score,
      icon: config.icon,
      category: category.category,
      matchedCount: category.matchedItems.length,
      totalCount: category.matchedItems.length + category.missingItems.length
    };
  }

  private buildRadarChart(response: JobMatchingResponse): void {
    const categories = response.matchCategories.filter(c => c.weight > 0);
    const labels = categories.map(c => this.categoryConfig[c.category].translationKey);
    const scores = categories.map(c => c.score);
    const colors = categories.map(c => this.categoryConfig[c.category].color1);

    this.radarData = {
      labels: labels,
      datasets: [
        {
          label: 'Your Match Score',
          data: scores,
          backgroundColor: 'rgba(16, 185, 129, 0.2)',
          borderColor: '#10b981',
          pointBackgroundColor: '#10b981',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#10b981'
        },
        {
          label: 'Job Requirements',
          data: categories.map(() => 100),
          backgroundColor: 'rgba(107, 114, 128, 0.1)',
          borderColor: 'rgba(107, 114, 128, 0.5)',
          pointBackgroundColor: 'rgba(107, 114, 128, 0.5)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(107, 114, 128, 0.5)'
        }
      ]
    };

    this.radarOptions = {
      plugins: {
        legend: {
          display: true,
          position: 'bottom',
          labels: {
            color: 'rgba(255, 255, 255, 0.7)'
          }
        }
      },
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: {
            display: true,
            stepSize: 25,
            color: 'rgba(255, 255, 255, 0.5)',
            backdropColor: 'transparent'
          },
          grid: {
            color: 'rgba(156, 163, 175, 0.3)',
            lineWidth: 1
          },
          angleLines: {
            display: true,
            color: 'rgba(156, 163, 175, 0.3)',
            lineWidth: 1
          },
          pointLabels: {
            display: true,
            color: 'rgba(255, 255, 255, 0.8)',
            font: {
              size: 11
            }
          }
        }
      },
      maintainAspectRatio: false
    };
  }

  openCategoryDetails(category: MatchCategoryType): void {
    if (!this.matchingResponse) return;
    
    this.selectedCategory = this.matchingResponse.matchCategories.find(c => c.category === category) || null;
    this.selectedCategoryConfig = this.categoryConfig[category];
    this.showDetailsDialog = true;
    this.viewDetailsClick.emit(category);
  }

  closeDetailsDialog(): void {
    this.showDetailsDialog = false;
    this.selectedCategory = null;
  }

  getScoreClass(score: number): string {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  }

  getScoreBgClass(score: number): string {
    if (score >= 80) return 'bg-green-500/20';
    if (score >= 60) return 'bg-yellow-500/20';
    if (score >= 40) return 'bg-orange-500/20';
    return 'bg-red-500/20';
  }

  getMatchStrengthClass(strength: string): string {
    switch (strength) {
      case 'exact': return 'text-green-400 bg-green-500/20';
      case 'strong': return 'text-emerald-400 bg-emerald-500/20';
      case 'partial': return 'text-yellow-400 bg-yellow-500/20';
      case 'weak': return 'text-orange-400 bg-orange-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  }

  getMatchStrengthOrder(strength: string): number {
    switch (strength) {
      case 'exact': return 1;
      case 'strong': return 2;
      case 'partial': return 3;
      case 'weak': return 4;
      default: return 5;
    }
  }

  getSortedMatchedItems(): MatchedItem[] {
    if (!this.selectedCategory) return [];
    return [...this.selectedCategory.matchedItems].sort((a, b) => 
      this.getMatchStrengthOrder(a.matchStrength) - this.getMatchStrengthOrder(b.matchStrength)
    );
  }

  getFullMatches(): MatchedItem[] {
    return this.getSortedMatchedItems().filter(item => 
      item.matchStrength === 'exact' || item.matchStrength === 'strong'
    );
  }

  getPartialMatches(): MatchedItem[] {
    return this.getSortedMatchedItems().filter(item => 
      item.matchStrength === 'partial' || item.matchStrength === 'weak'
    );
  }

  getImportanceClass(importance: string): string {
    switch (importance) {
      case 'required': return 'text-red-400 bg-red-500/20';
      case 'preferred': return 'text-yellow-400 bg-yellow-500/20';
      case 'nice-to-have': return 'text-blue-400 bg-blue-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  }

  getImpactSeverity(impact: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' | 'contrast' {
    switch (impact) {
      case 'high': return 'danger';
      case 'medium': return 'warn';
      case 'low': return 'info';
      default: return 'secondary';
    }
  }

  onUpdateProfileClick(): void {
    this.updateProfileClick.emit();
  }

  onViewDetails(category: MatchCategoryType): void {
    this.openCategoryDetails(category);
  }

  onRecommendationClick(recommendation: MatchRecommendation): void {
    this.recommendationClick.emit(recommendation);
  }
}
