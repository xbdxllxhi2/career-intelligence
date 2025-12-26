import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environments';
import { JobOffer } from '../models/interface/job-offer';
import { Observable, of } from 'rxjs';
import { Page } from '../models/interface/page';
import { PageRequest } from '../models/interface/page-request';

@Injectable({
  providedIn: 'root',
})
export class JobService {
  private readonly apiUrl = environment.apiUrl+ "/jobs";

  dummy = [
    {
      title: 'Backend Engineer',
      company: 'Proxym Group',
      location: 'Nouakchott',
      description: 'lorem ipsum dolor sit amet consectetur adipiscing elit lorem ipsum dolor sit amet consectetur adipiscing elit lorem ipsum dolor sit amet consectetur adipiscing elit',
      logo: 'https://via.placeholder.com/40?text=P'
    },
    {
      title: 'Frontend Engineer',
      company: 'Acme Inc',
      location: 'Paris',
      description: 'Work on Angular projects',
      logo: 'https://via.placeholder.com/40?text=A'
    },
    {
      title: 'Full Stack Developer',
      company: 'Tech Corp',
      location: 'Remote',
      description: 'Angular + Node.js',
      logo: 'https://via.placeholder.com/40?text=T'
    },
  ];

  constructor(private client: HttpClient) {
  }


  getJobs(query: PageRequest): Observable<Page<JobOffer>> {
    return this.client.get<Page<JobOffer>>(`${this.apiUrl}`, {params:{"page":query.page,"size":query.size}});
  }

  getJobDetails(reference:string): Observable<JobOffer>{
    return this.client.get<JobOffer>(`${this.apiUrl}/${reference}`)
  }
}
