import { Component, Input } from '@angular/core';
import { TextareaModule } from 'primeng/textarea';
import { FormsModule } from '@angular/forms';
import { AccordionModule } from 'primeng/accordion';
import { SplitterModule } from 'primeng/splitter';
import { QuestionAnswer } from '../../models/interface/question-answer';
import { ButtonModule } from 'primeng/button';
import { HttpClientModule } from '@angular/common/http';
import { FileUploadModule } from 'primeng/fileupload';
import { InputGroupModule } from 'primeng/inputgroup';
import { InputGroupAddonModule } from 'primeng/inputgroupaddon';
import { IftaLabelModule } from 'primeng/iftalabel';
import { InplaceModule } from 'primeng/inplace';
import { CvProfile } from '../../models/interface/cv-profile';
import { SkeletonModule } from 'primeng/skeleton';

@Component({
  selector: 'app-profile',
  imports: [TextareaModule, FormsModule, AccordionModule, SplitterModule, ButtonModule,
    FileUploadModule, HttpClientModule, InputGroupModule, InputGroupAddonModule, IftaLabelModule,InplaceModule,
  SkeletonModule],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile {
  @Input() conversation: QuestionAnswer[] = [];
  textareaValue: string = '';
  profileData: CvProfile = {
    firstName: '',
    lastName: '',
    title: '',
    summary: '',
    contact: {
      email: '',
      phone: ''
    },
    location: {
      city: '',
      country: ''
    },
    languages: []
  };

  submitQuestion() {
  }

  isConversationEmpty(): boolean {
    return this.conversation.length === 0;
  }


  getConversation(): QuestionAnswer[] {
    return this.conversation;
  }

  handleUpload(event: any) {
    console.log('Files uploaded:', event.files);
  }
}
