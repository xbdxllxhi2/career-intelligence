import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { UserProfile } from '../models/interface/cv-profile';
import { environment } from '../environments/environments';
import { Observable } from 'rxjs';

export interface ParsedProfile {
  firstName?: string;
  lastName?: string;
  phone?: string;
  city?: string;
  country?: string;
  email?: string;
  linkedin?: string;
  github?: string;
  summary?: string;
  education?: Array<{
    degree: string;
    school?: string;
    institution?: string;
    year: string;
    coursework?: string;
  }>;
  experience?: Array<{
    title: string;
    company?: string;
    period?: string;
    location?: string;
    tags?: string[];
    bullets?: string[];
  }>;
  projects?: Array<{
    name: string;
    description?: string;
    url?: string;
    year?: string;
    tags?: string[];
    bullets?: string[];
  }>;
  languages?: Array<{
    name: string;
    proficiency: string;
  }>;
}

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
  
  /**
   * Upload a resume file and parse it to extract profile data
   * @param file The resume file (PDF or DOCX)
   * @returns Parsed profile data
   */
  parseResume(file: File): Observable<ParsedProfile> {
    const formData = new FormData();
    formData.append('file', file);
    return this.client.post<ParsedProfile>(`${this.apiUrl}/parse-resume`, formData);
  }

}
