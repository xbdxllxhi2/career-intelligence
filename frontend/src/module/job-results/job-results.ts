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
import { JobMatchingResponse, MatchCategoryType, MatchRecommendation } from '../../models/interface/job-matching';
import { Router } from '@angular/router';


@Component({
  selector: 'app-job-results',
  imports: [CardModule, ButtonModule, DrawerModule, JobAddressPipe, TagModule, PanelModule, MeterGroupModule, DatePipe,
    ChartModule, CommonModule ,ProgressSpinnerModule, ToastModule, ChipModule,PaginatorModule, ApplicationInfoModal, TranslocoModule, JobMatchingStats],
  providers: [MessageService],
  templateUrl: './job-results.html',
  styleUrl: './job-results.scss',
})
export class JobResults implements OnChanges {
  @Input({required:true}) resultsData!: Page<JobOffer>;
  @Input() selectedJobRef: string | null = null;
  @Input() sideFilterActive: boolean = false;
  @Output() closeResults = new EventEmitter<void>();
  @Output() isjobDetailsOpen = new EventEmitter<boolean>();
  @Output() onPageChangeEvent = new EventEmitter<PaginatorState>();
  @Output() onJobSelected = new EventEmitter<string>();

  generatingCv: boolean = false;
  selectedJob: JobOffer | null = null;
  gridView: boolean = false;

  visible: boolean = false;

  showApplicationModalFlag!: boolean;

  // Job matching data
  matchingResponse: JobMatchingResponse | null = null;
  matchingLoading: boolean = false;

  constructor(
    private jobService: JobService, 
    private resumeService: ResumeService, 
    private messageService: MessageService,
    private jobMatchingService: JobMatchingService,
    private router: Router
  ) {}

  ngOnInit() {
    this.showApplicationModalFlag = false;
  }

  ngOnChanges(changes: SimpleChanges) {
    // Load job details if selectedJobRef is provided (e.g., from URL on refresh)
    if (changes['selectedJobRef'] && this.selectedJobRef) {
      this.loadJobFromRef(this.selectedJobRef);
    }
  }

  private loadJobFromRef(jobRef: string) {
    this.jobService.getJobDetails(jobRef).subscribe({
      next: (data) => {
        this.selectedJob = data;
        this.visible = true;
        this.isjobDetailsOpen.emit(true);
        this.loadJobMatching(jobRef);
      },
      error: (err) => {
        console.log('Failed to load job from URL:', err);
      }
    });
  }

  private loadJobMatching(jobRef: string) {
    this.matchingLoading = true;
    this.matchingResponse = null;
    this.jobMatchingService.getJobMatching(jobRef).subscribe({
      next: (response) => {
        this.matchingResponse = response;
        this.matchingLoading = false;
      },
      error: (err) => {
        console.log('Failed to load job matching:', err);
        this.matchingLoading = false;
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


  getSelectedJob(): JobOffer | null {
    return this.selectedJob ? this.selectedJob : null;
  }

  showJobDetails(reference: string) {
    this.emitJobDetailEvent(true);
    this.onJobSelected.emit(reference);
    this.jobService.getJobDetails(reference)
      .subscribe({
        next: (data) => {
          this.selectedJob = data;
          this.loadJobMatching(reference);
        }, error: (err) => {
          console.log(err)
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
