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


@Component({
  selector: 'app-job-results',
  imports: [CardModule, ButtonModule, DrawerModule, JobAddressPipe, TagModule, PanelModule, MeterGroupModule, DatePipe,
    ChartModule, CommonModule ,ProgressSpinnerModule, ToastModule, ChipModule,PaginatorModule, ApplicationInfoModal],
  providers: [MessageService],
  templateUrl: './job-results.html',
  styleUrl: './job-results.scss',
})
export class JobResults implements OnChanges {
  @Input({required:true}) resultsData!: Page<JobOffer>;
  @Input() selectedJobRef: string | null = null;
  @Output() closeResults = new EventEmitter<void>();
  @Output() isjobDetailsOpen = new EventEmitter<boolean>();
  @Output() onPageChangeEvent = new EventEmitter<PaginatorState>();
  @Output() onJobSelected = new EventEmitter<string>();

  generatingCv: boolean = false;
  selectedJob: JobOffer | null = null;

  visible: boolean = false;

  showApplicationModalFlag!: boolean;

  constructor(private jobService: JobService, private resumeService: ResumeService, private messageService: MessageService) {
  }

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
      },
      error: (err) => {
        console.log('Failed to load job from URL:', err);
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


  value = [
    { label: 'Apps', color1: '#34d399', color2: '#fbbf24', value: 25, icon: 'pi pi-table' },
    { label: 'Messages', color1: '#fbbf24', color2: '#60a5fa', value: 15, icon: 'pi pi-inbox' },
    { label: 'Media', color1: '#60a5fa', color2: '#c084fc', value: 20, icon: 'pi pi-image' },
    { label: 'System', color1: '#c084fc', color2: '#c084fc', value: 10, icon: 'pi pi-cog' }
  ];


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
