import { Component } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { ApplicationStatus, UserApplicationInfo } from '../../models/interface/application-info';

@Component({
  selector: 'app-applications',
  imports: [ButtonModule],
  templateUrl: './applications.html',
  styleUrl: './applications.scss',
})
export class Applications {

  userApplications=[
      {
        reference:"edf",
        jobReference:"",
        date: new Date(),
        portal:"",
        rating: 1,
        uploadedResumeReference:"",
        notes:"",
        status:ApplicationStatus.APPLIED
      }
    ];


  // getUserApplications(): UserApplicationInfo[] {
  //   return 
  // }
}
