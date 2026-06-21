import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { TextareaModule } from 'primeng/textarea';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { ResumeService } from '../../service/resume-service';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { TranslocoModule, TranslocoService } from '@jsverse/transloco';
import { KeycloakService } from 'keycloak-angular';
import { environment } from '../../environments/environments';

@Component({
  selector: 'app-resume',
  imports: [TextareaModule, ButtonModule, ToggleSwitchModule, FormsModule, ToastModule, TranslocoModule],
  templateUrl: './resume.html',
  providers: [MessageService],
  styleUrl: './resume.scss',
})
export class Resume implements OnInit {
  private translocoService = inject(TranslocoService);
  private keycloak = inject(KeycloakService);

  isAuthenticated = false;
  offerDescription!: string;
  isGeneratingResume!: boolean;
  enableReview = false;

  constructor(private resumeService: ResumeService, private messageService: MessageService) {}

  ngOnInit(): void {
    this.isAuthenticated = environment.keycloak.enabled ? this.keycloak.isLoggedIn() : true;
    this.offerDescription = '';
    this.isGeneratingResume = false;
  }

  login(): void {
    this.keycloak.login({
      redirectUri: window.location.origin + '/resume'
    });
  }

  generateResume() {
    this.isGeneratingResume = true;
    this.resumeService.generateResumeFromDescription(this.offerDescription, this.enableReview).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        this.messageService.add({
          summary: 'Error',
          detail: 'Try again later...',
          severity: 'error',
        });
        this.isGeneratingResume = false;
      },
      complete: () => {
        this.isGeneratingResume = false;
      },
    });
  }
}
