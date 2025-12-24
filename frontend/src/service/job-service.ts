import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environments';
import { JobOffer } from '../models/interface/job-offer';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class JobService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private client:HttpClient){
  }


 getJobsByAskingAI(query:String): Observable<JobOffer[]> {
  return of( [
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
      ]);

  // return this.client.get<JobOffer[]>(`${this.apiUrl}/jobs/ai`);
}
}
