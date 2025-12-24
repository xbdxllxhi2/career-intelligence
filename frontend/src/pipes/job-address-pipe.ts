import { Pipe, PipeTransform } from '@angular/core';
import { JobOffer } from '../models/interface/job-offer';

@Pipe({
  name: 'jobAddress'
})
export class JobAddressPipe implements PipeTransform {

  transform(job: JobOffer | null | undefined): unknown {
    if (!job) return '';

    const parts = [
      job.city,  
      // job.region, 
      job.country   
    ].filter(Boolean); 

    return parts.join(', ');
  }
}

