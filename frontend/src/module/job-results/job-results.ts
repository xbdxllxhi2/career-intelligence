import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CardModule } from 'primeng/card';
import { JobOffer } from '../../models/interface/job-offer';
import { ButtonModule } from 'primeng/button';
import { DrawerModule } from 'primeng/drawer';
import { JobAddressPipe } from '../../pipes/job-address-pipe';
import { JobService } from '../../service/job-service';

@Component({
  selector: 'app-job-results',
  imports: [CardModule, ButtonModule, DrawerModule, JobAddressPipe],
  templateUrl: './job-results.html',
  styleUrl: './job-results.scss',
})
export class JobResults {
  @Input() showResults: boolean = false;
  @Input() resultsData: JobOffer[] = [];
  @Output() closeResults = new EventEmitter<void>();
  
constructor(private jobService:JobService){

}

  selectedJob: JobOffer | null = null;

  visible: boolean = false;


  close() {
    this.closeResults.emit();
  }

  getSelectedJob(): JobOffer | null {
    return this.selectedJob ? this.selectedJob : null;
  }

  showJobDetails(reference:string){
      this.visible = true
      this.jobService.getJobDetails(reference)
      .subscribe({next:(data)=>{
        this.selectedJob = data;
      }, error:(err)=>{
        console.log(err)
      }})
  }
}
