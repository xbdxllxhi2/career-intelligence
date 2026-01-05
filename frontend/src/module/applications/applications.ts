import { Component, effect, OnInit, signal } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { ApplicationStatus, UserApplicationInfo } from '../../models/interface/application-info';
import { UserApplicationService } from '../../service/user-application-service';
import { PageRequest } from '../../models/interface/page-request';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

@Component({
  selector: 'app-applications',
  imports: [ButtonModule, ToastModule],
  templateUrl: './applications.html',
  styleUrl: './applications.scss',
  providers: [MessageService],
})
export class Applications implements OnInit {
  pageRequest: PageRequest = { size: 10, page: 0 };
  userApplications = signal<UserApplicationInfo[]>([]);

  constructor(
    private userAppSerice: UserApplicationService,
    private primengMessageService: MessageService
  ) {}

  ngOnInit() {
    this.getUserApplications();
  }

  getUserApplications() {
    this.userAppSerice.getApplications(this.pageRequest).subscribe({
      next: (data) => {
        this.userApplications.set(data);
      },
      error: (err) => {
        this.primengMessageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to get applications.',
        });
      },
    });
  }
}
