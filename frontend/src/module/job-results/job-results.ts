import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CardModule } from 'primeng/card';
import { JobOffer } from '../../models/interface/job-offer';
import { ButtonModule } from 'primeng/button';
import { DrawerModule } from 'primeng/drawer';

@Component({
  selector: 'app-job-results',
  imports: [CardModule, ButtonModule, DrawerModule],
  templateUrl: './job-results.html',
  styleUrl: './job-results.scss',
})
export class JobResults {
  @Input() showResults  :boolean = false;
  @Input() resultsData  :JobOffer[] = [];
   @Output() closeResults = new EventEmitter<void>();

   visible : boolean = false;


  close() {
    this.closeResults.emit();
  }

  getSelectedJob(): JobOffer | null {
    return this.resultsData.length > 0 ? this.resultsData[0] : null;
  }
}
