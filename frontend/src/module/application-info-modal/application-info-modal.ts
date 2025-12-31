import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { FileUploadModule } from 'primeng/fileupload';
import { SelectModule } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { RatingModule } from 'primeng/rating';

import { ApplicationInfo } from '../../models/interface/application-info';

@Component({
  selector: 'app-application-info-modal',
  imports: [DialogModule, FileUploadModule, SelectModule, FormsModule, ButtonModule,RatingModule],
  templateUrl: './application-info-modal.html',
  styleUrl: './application-info-modal.scss',
})
export class ApplicationInfoModal {
  @Input({required: true})  applicationModalVisible!: boolean ;
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


  onModalUpload($event: any) {
    console.log($event);
  }

  onModalClose(){
    this.modalCloseEvent.emit();
  }

  saveApplicationInfo() {
    let modalInfo : ApplicationInfo = {
      portal: this.selectedApplicationPortal,
      rating: this.ratingValue
    }

    this.modalSer
    
 
       this.onModalClose()
  }

  cancelApplicationInfo() {
    this.onModalClose()
  }
}
