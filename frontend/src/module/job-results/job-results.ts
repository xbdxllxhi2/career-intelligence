import { Component, EventEmitter, Input, Output, OnChanges, SimpleChanges } from '@angular/core';
import { CardModule } from 'primeng/card';
import { JobOffer } from '../../models/interface/job-offer';
import { ButtonModule } from 'primeng/button';
import { DrawerModule } from 'primeng/drawer';
import { JobAddressPipe } from '../../pipes/job-address-pipe';
import { JobService } from '../../service/job-service';
import { CommonModule, DatePipe } from '@angular/common';
import { TagModule } from 'primeng/tag';
import { PanelModule } from 'primeng/panel';
import { MeterGroupModule } from 'primeng/metergroup';
import { ChartModule } from 'primeng/chart';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { SkeletonModule } from 'primeng/skeleton';
import { ResumeService } from '../../service/resume-service';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { ChipModule } from 'primeng/chip';
import { PaginatorState } from 'primeng/types/paginator';
import { PaginatorModule } from 'primeng/paginator';
import { Page } from '../../models/interface/page';
import { ApplicationInfoModal } from '../application-info-modal/application-info-modal';
import { TranslocoModule } from '@jsverse/transloco';
import { JobMatchingStats } from '../../shared/job-matching-stats/job-matching-stats';
import { JobMatchingService } from '../../service/job-matching-service';
import { JobMatchingResponse, MatchCategoryType, MatchRecommendation, MissingItem } from '../../models/interface/job-matching';
import { Router } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';
import { DialogModule } from 'primeng/dialog';
import { DividerModule } from 'primeng/divider';


@Component({
  selector: 'app-job-results',
  imports: [CardModule, ButtonModule, DrawerModule, JobAddressPipe, TagModule, PanelModule, MeterGroupModule, DatePipe,
    ChartModule, CommonModule, ProgressSpinnerModule, SkeletonModule, ToastModule, ChipModule, PaginatorModule, ApplicationInfoModal, TranslocoModule, JobMatchingStats, DialogModule, DividerModule],
  providers: [MessageService],
  templateUrl: './job-results.html',
  styleUrl: './job-results.scss',
})
export class JobResults implements OnChanges {
  @Input({required:true}) resultsData!: Page<JobOffer>;
  @Input() selectedJobRef: string | null = null;
  @Input() sideFilterActive: boolean = false;
  @Input() isAuthenticated: boolean = false;
  @Input() isLoadingJobs: boolean = false;
  @Output() closeResults = new EventEmitter<void>();
  @Output() isjobDetailsOpen = new EventEmitter<boolean>();
  @Output() onPageChangeEvent = new EventEmitter<PaginatorState>();
  @Output() onJobSelected = new EventEmitter<string>();

  generatingCv: boolean = false;
  selectedJob: JobOffer | null = null;
  gridView: boolean = false;
  private loadingJobRef: string | null = null;  // Track which job is being loaded
  isLoadingJobDetails: boolean = false;

  visible: boolean = false;

  showApplicationModalFlag!: boolean;

  // Job matching data
  matchingResponse: JobMatchingResponse | null = null;
  matchingLoading: boolean = false;
  matchingError: string | null = null;

  // Full report dialog
  showFullReportDialog: boolean = false;
  fullReportData: JobMatchingResponse | null = null;

  constructor(
    private jobService: JobService, 
    private resumeService: ResumeService, 
    private messageService: MessageService,
    private jobMatchingService: JobMatchingService,
    private router: Router,
    private keycloak: KeycloakService
  ) {}

  ngOnInit() {
    this.showApplicationModalFlag = false;
  }

  login(): void {
    this.keycloak.login({
      redirectUri: window.location.href
    });
  }

  ngOnChanges(changes: SimpleChanges) {
    // Load job details if selectedJobRef is provided (e.g., from URL on refresh)
    // Skip if the job is already loaded or currently being loaded
    if (changes['selectedJobRef'] && this.selectedJobRef) {
      const alreadyLoaded = this.selectedJob?.reference === this.selectedJobRef;
      const currentlyLoading = this.loadingJobRef === this.selectedJobRef;
      if (!alreadyLoaded && !currentlyLoading) {
        this.loadJobFromRef(this.selectedJobRef);
      }
    }
  }

  private loadJobFromRef(jobRef: string) {
    this.loadingJobRef = jobRef;
    this.isLoadingJobDetails = true;
    this.jobService.getJobDetails(jobRef).subscribe({
      next: (data) => {
        this.selectedJob = data;
        this.visible = true;
        this.isjobDetailsOpen.emit(true);
        this.isLoadingJobDetails = false;
        if (this.isAuthenticated) {
          this.loadJobMatching(jobRef);
        }
      },
      error: (err) => {
        console.log('Failed to load job from URL:', err);
        this.isLoadingJobDetails = false;
      }
    });
  }

  private loadJobMatching(jobRef: string) {
    this.matchingLoading = true;
    this.matchingResponse = null;
    this.matchingError = null;
    this.jobMatchingService.getJobMatching(jobRef).subscribe({
      next: (response) => {
        this.matchingResponse = response;
        this.matchingLoading = false;
      },
      error: (err) => {
        console.log('Failed to load job matching:', err);
        this.matchingLoading = false;
        if (err.status === 404) {
          this.matchingError = 'Complete your profile to see how well you match this job.';
        } else {
          this.matchingError = 'Unable to load matching analysis. Please try again later.';
        }
      }
    });
  }


  emitJobDetailEvent(isOpen: boolean): void {
    this.visible = true
    this.isjobDetailsOpen.emit(isOpen);
  }

  showApplicationModal() {
    this.showApplicationModalFlag = true;
  }

  onModalClose() {
    this.showApplicationModalFlag = false;
  }


  onUpdateProfile(): void {
    this.router.navigate(['/profile']);
  }

  onViewMatchingDetails(category: MatchCategoryType): void {
    // Could open a modal with detailed matching info for this category
    console.log('View details for category:', category);
    this.messageService.add({ 
      summary: 'Category Details', 
      detail: `Viewing ${category} matching details`, 
      severity: 'info' 
    });
  }

  onRecommendationClick(recommendation: MatchRecommendation): void {
    // TODO: Handle recommendation action - could navigate to relevant section or open modal
    console.log('Recommendation clicked:', recommendation);
  }

  onViewFullReport(report: JobMatchingResponse): void {
    this.fullReportData = report;
    this.showFullReportDialog = true;
  }

  getScoreClass(score: number): string {
    if (score >= 75) return 'text-green-400';
    if (score >= 30) return 'text-yellow-400';
    return 'text-red-400';
  }

  getScoreBgClass(score: number): string {
    if (score >= 75) return 'bg-green-900/30';
    if (score >= 30) return 'bg-yellow-900/30';
    return 'bg-red-900/30';
  }

  getImpactSeverity(impact: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' {
    switch (impact) {
      case 'high': return 'danger';
      case 'medium': return 'warn';
      case 'low': return 'info';
      default: return 'secondary';
    }
  }

  getImportanceSeverity(importance: string): 'success' | 'info' | 'warn' | 'danger' | 'secondary' {
    switch (importance) {
      case 'required': return 'danger';
      case 'preferred': return 'warn';
      case 'nice-to-have': return 'info';
      default: return 'secondary';
    }
  }

  getAllMissingItems(): MissingItem[] {
    if (!this.fullReportData) return [];
    return this.fullReportData.matchCategories
      .flatMap(cat => cat.missingItems)
      .sort((a, b) => {
        const order = { 'required': 0, 'preferred': 1, 'nice-to-have': 2 };
        return (order[a.importance] ?? 3) - (order[b.importance] ?? 3);
      });
  }


  getSelectedJob(): JobOffer | null {
    return this.selectedJob ? this.selectedJob : null;
  }

  async shareJob(job: JobOffer): Promise<void> {
    const shareUrl = `${window.location.origin}/jobs/${job.reference}`;
    const shareData = {
      title: job.title,
      text: `Check out this job: ${job.title}${job.company ? ' at ' + job.company : ''}`,
      url: shareUrl
    };

    // Try Web Share API first (mobile and some desktop browsers)
    if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
      try {
        await navigator.share(shareData);
        return;
      } catch (err) {
        // User cancelled or error - fall back to clipboard
        if ((err as Error).name === 'AbortError') return;
      }
    }

    // Fallback: copy link to clipboard
    try {
      await navigator.clipboard.writeText(shareUrl);
      this.messageService.add({
        severity: 'success',
        summary: 'Link Copied',
        detail: 'Job link copied to clipboard',
        life: 3000
      });
    } catch (err) {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to copy link',
        life: 3000
      });
    }
  }

  showJobDetails(reference: string) {
    this.loadingJobRef = reference;  // Mark as loading to prevent duplicate from ngOnChanges
    this.isLoadingJobDetails = true;
    this.emitJobDetailEvent(true);
    this.onJobSelected.emit(reference);
    this.jobService.getJobDetails(reference)
      .subscribe({
        next: (data) => {
          this.selectedJob = data;
          this.isLoadingJobDetails = false;
          if (this.isAuthenticated) {
            this.loadJobMatching(reference);
          }
        }, error: (err) => {
          console.log(err);
          this.isLoadingJobDetails = false;
        }
      })
  }


  generateResume(job: JobOffer) {
    this.generatingCv = true
    this.resumeService.generateResume(job.reference)
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = job.company + '_cv.pdf';
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
        }, error: (err) => {
          this.messageService.add({ summary: "Error", detail: "Try again later...", severity: "error" });
          this.generatingCv = false
        },
        complete: () => { this.generatingCv = false }
      });
  }


  //Paginator
  onPageChange(event: PaginatorState) {
    this.onPageChangeEvent.emit(event)
  }


  // Radar
  title = 'GFG';
  data = {
    labels: ['GeeksforGeeks', 'Tutorial Point', 'W3 Schools',
      'Javatpoint', 'Indiabix', 'Codechef', 'Hackerrank'],
    datasets: [
      {
        label: 'First Dataset',
        data: [75, 49, 95, 71, 66, 65, 45],
        // backgroundColor: 'lightgreen',
        borderColor: 'lightgreen',
        pointHoverBorderColor: 'lightgreen',

      },
      {
        label: 'Second dataset',
        data: [85, 99, 75, 41, 86, 56, 55],
        // backgroundColor: 'none',
        borderColor: 'white',
        pointHoverBorderColor: 'white',
      }
    ]
  };

  options = {
    scales: {
      r: {                 // 'r' is the radial scale for radar charts
        ticks: {
          display: false   // hides the numbers on each circular level
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.5)',
          lineWidth: 2,
          display: true    // keeps the circular grid lines if you want
        },
        angleLines: {
          display: true,   // keeps the spokes (lines from center to labels)
          color: 'rgba(122, 126, 133, 0.7)', // radial lines from center
          lineWidth: 1.5
        },
        pointLabels: {
          display: true    // keeps labels like "Eating", "Drinking"
        }
      }
    },
    plugins: {
      legend: {
        display: true
      }
    }
  };
}
