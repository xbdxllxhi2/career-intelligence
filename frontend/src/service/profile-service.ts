import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { UserProfile } from '../models/interface/cv-profile';
import { environment } from '../environments/environments';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ProfileService {
  apiUrl:string = environment.apiUrl + "/user/profile"

  constructor(private client: HttpClient){}

  updateProfile(profile:UserProfile): Observable<void>{
    return this.client.put<void>(this.apiUrl,profile);
  }

  getUserProfile():Observable<UserProfile>{
    return this.client.get<UserProfile>(this.apiUrl);
  }
  

}
