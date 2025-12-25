import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class ResumeService {
  private readonly apiUrl = environment.apiUrl +"/resume";
  constructor(private client: HttpClient) { }

  generateResume(jobReference: string): Observable<Blob> {
    return this.client.post(`${this.apiUrl}`, { job_reference: jobReference },{
      responseType: 'blob'  
    });
  }
}
