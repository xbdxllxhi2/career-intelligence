import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environments';
import { JobOffer } from '../models/interface/job-offer';
import { Observable, of } from 'rxjs';
import { Page } from '../models/interface/page';
import { PageRequest } from '../models/interface/page-request';
import { JobFilters } from '../models/filters/job-filters';
import { FilterOptions } from '../models/filters/filter-options';

@Injectable({
  providedIn: 'root',
})
export class JobService {
  private readonly apiUrl = environment.apiUrl+ "/jobs";

  constructor(private client: HttpClient) {
  }


  getJobs(query: PageRequest, filters: JobFilters | undefined): Observable<Page<JobOffer>> {
    // Clean filters - remove undefined, null, and empty string values
    const cleanFilters: Record<string, any> = {};
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          cleanFilters[key] = value;
        }
      });
    }
    return this.client.get<Page<JobOffer>>(`${this.apiUrl}`, {
      params: { page: query.page, size: query.size, ...cleanFilters }
    });
  }

  getJobDetails(reference:string): Observable<JobOffer>{
    return this.client.get<JobOffer>(`${this.apiUrl}/${reference}`)
  }

  getFilterOptions(): Observable<FilterOptions> {
    return this.client.get<FilterOptions>(`${this.apiUrl}/filters/options`);
  }
}
