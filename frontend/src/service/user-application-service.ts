import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { PageRequest, toHttpParams } from '../models/interface/page-request';
import { ApplicationInfo, saveApplicationRequest } from '../models/interface/application-info';
import { environment } from '../environments/environments';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class UserApplicationService {
  
  apiUrl = environment.apiUrl + '/user/application';

  constructor(private client: HttpClient) {}

  getApplications(request:PageRequest): Observable<ApplicationInfo[]> {
    let params = toHttpParams(request)
    return this.client.get<ApplicationInfo[]>(`${this.apiUrl}`, {params: params});
  }


  getApplicationById(id: string) : Observable<ApplicationInfo> {
    return this.client.get<ApplicationInfo>(`${this.apiUrl}/${id}`);
  }

  saveApplication(applicationData: saveApplicationRequest){
    return this.client.post(this.apiUrl, applicationData);
  }
}
