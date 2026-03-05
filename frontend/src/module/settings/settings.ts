import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { ToastModule } from 'primeng/toast';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { DialogModule } from 'primeng/dialog';
import { MessageService, ConfirmationService } from 'primeng/api';
import { KeycloakService } from 'keycloak-angular';
import { environment } from '../../environments/environments';
import { TranslocoModule } from '@jsverse/transloco';

interface PrivacySettings {
  analyticsEnabled: boolean;
  profileVisible: boolean;
  shareDataWithPartners: boolean;
}

interface CommunicationSettings {
  emailNotifications: boolean;
  jobAlerts: boolean;
  weeklyDigest: boolean;
  marketingEmails: boolean;
}

interface CookieSettings {
  necessary: boolean; // Always true, cannot be disabled
  functional: boolean;
  analytics: boolean;
  marketing: boolean;
}

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    ToggleSwitchModule,
    ToastModule,
    ConfirmDialogModule,
    DialogModule,
    TranslocoModule
  ],
  providers: [MessageService, ConfirmationService],
  templateUrl: './settings.html',
  styleUrl: './settings.scss'
})
export class Settings implements OnInit {
  private keycloak = inject(KeycloakService);
  private messageService = inject(MessageService);
  private confirmationService = inject(ConfirmationService);

  isAuthenticated = false;
  userEmail = '';

  // Privacy Settings
  privacySettings: PrivacySettings = {
    analyticsEnabled: true,
    profileVisible: true,
    shareDataWithPartners: false
  };

  // Communication Preferences
  communicationSettings: CommunicationSettings = {
    emailNotifications: true,
    jobAlerts: true,
    weeklyDigest: false,
    marketingEmails: false
  };

  // Cookie Preferences
  cookieSettings: CookieSettings = {
    necessary: true,
    functional: true,
    analytics: true,
    marketing: false
  };

  // Dialog visibility
  showDeleteDialog = false;
  showExportDialog = false;
  deleteConfirmText = '';

  ngOnInit(): void {
    if (environment.keycloak.enabled) {
      this.isAuthenticated = this.keycloak.isLoggedIn();
      if (this.isAuthenticated) {
        this.keycloak.loadUserProfile().then(profile => {
          this.userEmail = profile.email || '';
        });
      }
    }
    this.loadSettings();
  }

  private loadSettings(): void {
    // Load settings from localStorage or API
    const savedPrivacy = localStorage.getItem('privacySettings');
    const savedCommunication = localStorage.getItem('communicationSettings');
    const savedCookies = localStorage.getItem('cookieSettings');

    if (savedPrivacy) {
      this.privacySettings = JSON.parse(savedPrivacy);
    }
    if (savedCommunication) {
      this.communicationSettings = JSON.parse(savedCommunication);
    }
    if (savedCookies) {
      this.cookieSettings = { ...JSON.parse(savedCookies), necessary: true };
    }
  }

  savePrivacySettings(): void {
    localStorage.setItem('privacySettings', JSON.stringify(this.privacySettings));
    this.messageService.add({
      severity: 'success',
      summary: 'Saved',
      detail: 'Privacy settings updated successfully'
    });
  }

  saveCommunicationSettings(): void {
    localStorage.setItem('communicationSettings', JSON.stringify(this.communicationSettings));
    this.messageService.add({
      severity: 'success',
      summary: 'Saved',
      detail: 'Communication preferences updated successfully'
    });
  }

  saveCookieSettings(): void {
    localStorage.setItem('cookieSettings', JSON.stringify(this.cookieSettings));
    this.messageService.add({
      severity: 'success',
      summary: 'Saved',
      detail: 'Cookie preferences updated successfully'
    });
    // Apply cookie settings (disable/enable tracking scripts)
    this.applyCookieSettings();
  }

  private applyCookieSettings(): void {
    // Disable Google Analytics if analytics cookies are disabled
    if (!this.cookieSettings.analytics) {
      // @ts-ignore
      window['ga-disable-' + environment.googleAnalyticsId] = true;
    }
  }

  // GDPR: Right to Data Portability
  exportData(): void {
    this.showExportDialog = true;
  }

  confirmExportData(): void {
    // In a real app, this would call an API to generate the export
    this.messageService.add({
      severity: 'info',
      summary: 'Export Started',
      detail: 'Your data export is being prepared. You will receive an email with a download link.'
    });
    this.showExportDialog = false;

    // TODO: Call API to export user data
    // this.settingsService.exportUserData().subscribe(...)
  }

  // GDPR: Right to be Forgotten
  deleteAccount(): void {
    this.showDeleteDialog = true;
    this.deleteConfirmText = '';
  }

  confirmDeleteAccount(): void {
    if (this.deleteConfirmText.toLowerCase() !== 'delete my account') {
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Please type "delete my account" to confirm'
      });
      return;
    }

    this.confirmationService.confirm({
      message: 'This action is irreversible. All your data will be permanently deleted within 30 days as per GDPR requirements.',
      header: 'Final Confirmation',
      icon: 'pi pi-exclamation-triangle',
      acceptButtonStyleClass: 'p-button-danger',
      accept: () => {
        // TODO: Call API to delete account
        // this.settingsService.deleteAccount().subscribe(...)
        this.messageService.add({
          severity: 'success',
          summary: 'Account Deletion Requested',
          detail: 'Your account will be deleted within 30 days. You will receive a confirmation email.'
        });
        this.showDeleteDialog = false;

        // Logout after deletion request
        setTimeout(() => {
          if (environment.keycloak.enabled) {
            this.keycloak.logout(window.location.origin);
          }
        }, 3000);
      }
    });
  }

  // GDPR: Right to Access - View what data we have
  viewMyData(): void {
    // Navigate to a page showing all collected data
    this.messageService.add({
      severity: 'info',
      summary: 'Data Access',
      detail: 'Preparing your data overview...'
    });
    // TODO: Navigate to data overview page or open modal
  }

  login(): void {
    this.keycloak.login({
      redirectUri: window.location.origin + '/settings'
    });
  }
}
