import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { FloatLabel } from 'primeng/floatlabel';
import { TextareaModule } from 'primeng/textarea';
import { ResumeService } from '../../service/resume-service';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-resume',
  imports: [TextareaModule, FloatLabel, ButtonModule, FormsModule],
  templateUrl: './resume.html',
  providers:[MessageService],
  styleUrl: './resume.scss',
})
export class Resume implements OnInit {
  offerDescription!: string;
  isGeneratingResume!: boolean;

  constructor(private resumeService: ResumeService, private messageService:MessageService) {}

  ngOnInit(): void {
    this.offerDescription = '';
    this.isGeneratingResume=false;
  }

  generateResume() {
   this.isGeneratingResume = true
    this.resumeService.generateResumeFromDescription(this.offerDescription)
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'resume.pdf';
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
        }, error: (err) => {
          this.messageService.add({ summary: "Error", detail: "Try again later...", severity: "error" });
          this.isGeneratingResume = false
        },
        complete: () => { 
          this.isGeneratingResume = false }
      });
  }
}
