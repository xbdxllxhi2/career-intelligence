import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { PageRequest, toHttpParams } from '../models/interface/page-request';
import { UserApplicationInfo, saveApplicationRequest } from '../models/interface/application-info';
import { environment } from '../environments/environments';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class UserApplicationService {
  
  apiUrl = environment.apiUrl + '/user/applications';

  constructor(private client: HttpClient) {}

  getApplications(request:PageRequest): Observable<UserApplicationInfo[]> {
    let params = toHttpParams(request)
    return this.client.get<UserApplicationInfo[]>(`${this.apiUrl}`, {params: params});
  }


  getApplicationById(id: string) : Observable<UserApplicationInfo> {
    return this.client.get<UserApplicationInfo>(`${this.apiUrl}/${id}`);
  }

  saveApplication(applicationData: saveApplicationRequest){
    return this.client.post(this.apiUrl, applicationData);
  }
}
