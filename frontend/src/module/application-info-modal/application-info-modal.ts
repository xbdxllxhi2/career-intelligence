import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { FileUploadModule } from 'primeng/fileupload';
import { SelectModule } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { RatingModule } from 'primeng/rating';

import { UserApplicationInfo, saveApplicationRequest } from '../../models/interface/application-info';
import { UserApplicationService } from '../../service/user-application-service';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { JobOffer } from '../../models/interface/job-offer';

@Component({
  selector: 'app-application-info-modal',
  imports: [DialogModule, FileUploadModule, SelectModule, FormsModule, ButtonModule,RatingModule,ToastModule],
  templateUrl: './application-info-modal.html',
  styleUrl: './application-info-modal.scss',
})
export class ApplicationInfoModal {
  @Input({required: true})  applicationModalVisible!: boolean ;
  @Input({required:true}) selectedJob!: JobOffer;
  @Output() modalCloseEvent = new EventEmitter<void>();

  selectedApplicationPortal: string | undefined ;
  ratingValue: number = 0;

  applicationPortalOptions = [
    { name: 'LinkedIn', code: 'LI' },
    { name: 'Company Website', code: 'CW' },
    { name: 'Indeed', code: 'IN' },
    { name: 'Glassdoor', code: 'GD' },
    { name: 'Other', code: 'OT' },
    { name: "I don't know", code: 'IDK' },
  ];


  constructor(private userApplicaitonService: UserApplicationService, private primengMessageService: MessageService) {}

  onModalUpload($event: any) {
    console.log($event);
  }

  onModalClose(){
    this.modalCloseEvent.emit();
  }

  saveApplicationInfo() {
    let saveApplicationRequest: saveApplicationRequest = {
      job_reference: this.selectedJob.reference,
      date: new Date(),
      portal: this.selectedApplicationPortal || 'Other',
      rating: this.ratingValue,
      notes: '',
    }


    this.userApplicaitonService.saveApplication(saveApplicationRequest).subscribe({
      next: (response) => {
        this.primengMessageService.add({severity:'success', summary: 'Success', detail: 'Application information saved successfully.'});
      },
      error: (error) => {
        this.primengMessageService.add({severity:'error', summary: 'Error', detail: 'Failed to save application information.'});
      },complete: () => {
       this.onModalClose()
      }
    });
  }

  cancelApplicationInfo() {
    this.onModalClose()
  }
}
