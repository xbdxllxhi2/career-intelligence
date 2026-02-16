import { Component, OnInit } from '@angular/core';
import { TextareaModule } from 'primeng/textarea';
import { FormsModule } from '@angular/forms';
import { AccordionModule } from 'primeng/accordion';
import { SplitterModule } from 'primeng/splitter';
import { QuestionAnswer } from '../../models/interface/question-answer';
import { JobResults } from '../job-results/job-results';
import { JobOffer } from '../../models/interface/job-offer';
import { JobService } from '../../service/job-service';
import { JobsFilters } from '../jobs-filters/jobs-filters';
import { CommonModule } from '@angular/common';
import { PageRequest, toPageRequest } from '../../models/interface/page-request';
import { Page } from '../../models/interface/page';
import { PaginatorState } from 'primeng/paginator';
import { JobFilters } from '../../models/filters/job-filters';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-job-finder',
  imports: [
    TextareaModule,
    FormsModule,
    AccordionModule,
    SplitterModule,
    JobsFilters,
    JobResults,
    CommonModule,
  ],
  templateUrl: './job-finder.html',
  styleUrl: './job-finder.scss',
})
export class JobFinder implements OnInit {
  textareaValue: string = '';
  conversation: QuestionAnswer[] = [];
  showResults: boolean = true;
  filterSideLayout: boolean = true;
  selectedJobRef: string | null = null;

  pageRequest: PageRequest;
  resultsData: Page<JobOffer>;

  constructor(
    private service: JobService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.pageRequest = { page: 0, size: 10 };
    this.resultsData = {
      content: [],
      page: 0,
      size: 10,
      totalElements: 0,
      totalPages: 0,
    };
  }

  ngOnInit() {
    // Subscribe to query params to handle job reference from URL
    this.route.queryParams.subscribe(params => {
      const jobRef = params['job'];
      if (jobRef) {
        this.selectedJobRef = jobRef;
        this.filterSideLayout = false;
      }
    });

    this.getJobOffers(this.pageRequest);
  }

  isConversationEmpty(): boolean {
    return false;
  }

  onJobDetailsOpen(isOpen: boolean) {
    this.filterSideLayout = !isOpen;
    if (!isOpen) {
      // Remove job param from URL when closing details
      this.router.navigate([], {
        relativeTo: this.route,
        queryParams: { job: null },
        queryParamsHandling: 'merge'
      });
      this.selectedJobRef = null;
    }
  }

  onJobSelected(jobRef: string) {
    this.selectedJobRef = jobRef;
    // Update URL with job reference for refresh persistence
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { job: jobRef },
      queryParamsHandling: 'merge'
    });
  }

  getJobOffers(request: PageRequest, filters:JobFilters|undefined = undefined) {
    this.service.getJobs(request,filters).subscribe({
      next: (data) => {
        this.resultsData = data;
      },
      error: (err) => {
        console.log(err);
      },
    });
  }

  search(filters: JobFilters) {
    this.getJobOffers(this.pageRequest, filters);
  }


  onPageChangeEvent(event: PaginatorState) {
    this.pageRequest = toPageRequest(event.first, event.rows);
    this.getJobOffers(this.pageRequest);
  }

  getConversation(): QuestionAnswer[] {
    return [
      {
        question: 'What is the capital of France?',
        summary: "France's capital city is Paris.",
        reasoning:
          'Paris is the largest city in France and serves as the political, cultural, and economic center.',
        answer: 'Paris',
      },
      {
        question: 'How does photosynthesis work?',
        summary: 'Photosynthesis converts sunlight into chemical energy.',
        reasoning:
          'Plants absorb sunlight using chlorophyll, which converts carbon dioxide and water into glucose and oxygen.',
        answer:
          'Photosynthesis is the process by which plants make food using sunlight, water, and carbon dioxide.',
      },
      {
        question: 'What are the benefits of regular exercise?',
        summary: 'Exercise improves physical and mental health.',
        reasoning:
          'Regular activity strengthens muscles and bones, boosts cardiovascular health, and releases endorphins that improve mood.',
        answer:
          'Regular exercise enhances fitness, prevents diseases, and supports mental well-being.',
      },
      {
        question: 'Explain the theory of relativity in simple terms.',
        summary: "Einstein's theory explains how space, time, and gravity interact.",
        reasoning:
          'It shows that time and space are relative and affected by speed and mass, fundamentally changing our understanding of physics.',
        answer:
          'The theory of relativity describes how objects move and experience time differently depending on speed and gravity.',
      },
      {
        question: 'What is a blockchain?',
        summary: 'Blockchain is a decentralized digital ledger.',
        reasoning:
          'It records transactions across multiple computers securely, preventing data tampering without a central authority.',
        answer:
          'A blockchain is a distributed database that maintains a secure and transparent record of digital transactions.',
      },
    ];
  }
}
