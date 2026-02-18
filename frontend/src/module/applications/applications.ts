import { Component, computed, OnInit, signal } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { ApplicationStatus, UserApplicationInfo } from '../../models/interface/application-info';
import { UserApplicationService } from '../../service/user-application-service';
import { PageRequest } from '../../models/interface/page-request';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { DatePipe } from '@angular/common';
import { SelectModule } from 'primeng/select';
import { FormsModule } from '@angular/forms';

interface SortOption {
  label: string;
  value: string;
  direction: 'asc' | 'desc';
}

@Component({
  selector: 'app-applications',
  imports: [ButtonModule, ToastModule, DatePipe, SelectModule, FormsModule],
  templateUrl: './applications.html',
  styleUrl: './applications.scss',
  providers: [MessageService],
})
export class Applications implements OnInit {
  pageRequest: PageRequest = { size: 10, page: 0 };
  private rawApplications = signal<UserApplicationInfo[]>([]);
  
  sortOptions: SortOption[] = [
    { label: 'Date (Newest)', value: 'date', direction: 'desc' },
    { label: 'Date (Oldest)', value: 'date', direction: 'asc' },
    { label: 'Company (A-Z)', value: 'company', direction: 'asc' },
    { label: 'Company (Z-A)', value: 'company', direction: 'desc' },
    { label: 'Job Title (A-Z)', value: 'job_title', direction: 'asc' },
    { label: 'Status', value: 'status', direction: 'asc' },
  ];
  
  selectedSort: SortOption = this.sortOptions[0];
  
  userApplications = computed(() => {
    const apps = [...this.rawApplications()];
    const sort = this.selectedSort;
    
    return apps.sort((a, b) => {
      let comparison = 0;
      
      switch (sort.value) {
        case 'date':
          const dateA = a.date ? new Date(a.date).getTime() : 0;
          const dateB = b.date ? new Date(b.date).getTime() : 0;
          comparison = dateA - dateB;
          break;
        case 'company':
          comparison = (a.company || '').localeCompare(b.company || '');
          break;
        case 'job_title':
          comparison = (a.job_title || '').localeCompare(b.job_title || '');
          break;
        case 'status':
          comparison = (a.status || '').localeCompare(b.status || '');
          break;
      }
      
      return sort.direction === 'desc' ? -comparison : comparison;
    });
  });

  constructor(
    private userAppSerice: UserApplicationService,
    private primengMessageService: MessageService
  ) {}

  ngOnInit() {
    this.getUserApplications();
  }

  getUserApplications() {
    this.userAppSerice.getApplications(this.pageRequest).subscribe({
      next: (data) => {
        this.rawApplications.set(data);
      },
      error: (err) => {
        this.primengMessageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to get applications.',
        });
      },
    });
  }
  
  onSortChange() {
    // Trigger reactivity by creating a new reference
    this.rawApplications.set([...this.rawApplications()]);
  }
}
