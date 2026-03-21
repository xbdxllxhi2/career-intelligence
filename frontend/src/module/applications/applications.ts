import { Component, computed, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { ApplicationStatus, UserApplicationInfo } from '../../models/interface/application-info';
import { UserApplicationService } from '../../service/user-application-service';
import { PageRequest } from '../../models/interface/page-request';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { DatePipe } from '@angular/common';
import { SelectModule } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { TranslocoModule, TranslocoService } from '@jsverse/transloco';
import { toSignal } from '@angular/core/rxjs-interop';
import { KeycloakService } from 'keycloak-angular';
import { environment } from '../../environments/environments';
import { InputTextModule } from 'primeng/inputtext';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';

interface SortOption {
  label: string;
  value: string;
  direction: 'asc' | 'desc';
}

interface StatusFilter {
  label: string;
  value: string | null;
  icon: string;
  count?: number;
}

@Component({
  selector: 'app-applications',
  standalone: true,
  imports: [CommonModule, ButtonModule, ToastModule, DatePipe, SelectModule, FormsModule, TranslocoModule, InputTextModule, IconFieldModule, InputIconModule],
  templateUrl: './applications.html',
  styleUrl: './applications.scss',
  providers: [MessageService],
})
export class Applications implements OnInit {
  private translocoService = inject(TranslocoService);
  private keycloak = inject(KeycloakService);
  private activeLang = toSignal(this.translocoService.langChanges$, { initialValue: this.translocoService.getActiveLang() });

  isAuthenticated = false;
  searchQuery = '';
  selectedStatus: string | null = null;

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

  statusFilters: StatusFilter[] = [
    { label: 'All', value: null, icon: 'pi-list' },
    { label: 'Applied', value: 'APPLIED', icon: 'pi-send' },
    { label: 'Interview', value: 'INTERVIEW_SCHEDULED', icon: 'pi-calendar' },
    { label: 'Offer', value: 'ACCEPTED', icon: 'pi-check-circle' },
    { label: 'Rejected', value: 'REJECTED', icon: 'pi-times-circle' },
  ];

  selectedSort: SortOption = this.sortOptions[0];

  // Computed counts for each status
  statusCounts = computed(() => {
    const apps = this.rawApplications();
    return {
      all: apps.length,
      applied: apps.filter(a => a.status === 'APPLIED').length,
      interview: apps.filter(a => a.status === 'INTERVIEW_SCHEDULED').length,
      offer: apps.filter(a => a.status === 'ACCEPTED').length,
      rejected: apps.filter(a => a.status === 'REJECTED').length,
    };
  });

  userApplications = computed(() => {
    let apps = [...this.rawApplications()];
    const sort = this.selectedSort;

    // Filter by status
    if (this.selectedStatus) {
      apps = apps.filter(a => a.status === this.selectedStatus);
    }

    // Filter by search query
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase();
      apps = apps.filter(a =>
        a.job_title?.toLowerCase().includes(query) ||
        a.company?.toLowerCase().includes(query) ||
        a.job_city?.toLowerCase().includes(query)
      );
    }

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
    this.isAuthenticated = environment.keycloak.enabled ? this.keycloak.isLoggedIn() : true;
    if (this.isAuthenticated) {
      this.getUserApplications();
    }
  }

  login(): void {
    this.keycloak.login({
      redirectUri: window.location.origin + '/applications'
    });
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

  onStatusFilter(status: string | null) {
    this.selectedStatus = status;
    this.rawApplications.set([...this.rawApplications()]);
  }

  onSearch() {
    this.rawApplications.set([...this.rawApplications()]);
  }

  getStatusCount(status: string | null): number {
    if (status === null) return this.statusCounts().all;
    switch (status) {
      case 'APPLIED': return this.statusCounts().applied;
      case 'INTERVIEW_SCHEDULED': return this.statusCounts().interview;
      case 'ACCEPTED': return this.statusCounts().offer;
      case 'REJECTED': return this.statusCounts().rejected;
      default: return 0;
    }
  }
}
