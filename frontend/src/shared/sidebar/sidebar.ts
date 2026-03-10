import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DrawerModule } from 'primeng/drawer';
import { ButtonModule } from 'primeng/button';
import { BadgeModule } from 'primeng/badge';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { SelectModule } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { TranslocoService, TranslocoModule } from '@jsverse/transloco';
import { MenuModule } from 'primeng/menu';
import { PopoverModule } from 'primeng/popover';
import { KeycloakService } from 'keycloak-angular';
import { environment } from '../../environments/environments';
import { MenuItem } from 'primeng/api';

export interface Notification {
  id: string;
  title: string;
  message: string;
  time: Date;
  read: boolean;
  type: 'info' | 'success' | 'warning' | 'error';
}

interface Language {
  code: string;
  name: string;
  flag: string;
}

@Component({
  selector: 'app-sidebar',
  imports: [CommonModule, DrawerModule, ButtonModule, BadgeModule, RouterLink, RouterLinkActive, SelectModule, FormsModule, TranslocoModule, MenuModule, PopoverModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class Sidebar implements OnInit {
  private translocoService = inject(TranslocoService);
  private keycloak = inject(KeycloakService);
  
  visible = false;
  isAuthenticated = false;
  userName = '';
  userInitials = '';

  userMenuItems: MenuItem[] = [];

  notifications: Notification[] = [];

  languages: Language[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' }
  ];

  selectedLanguage: Language = this.languages.find(l => l.code === this.translocoService.getActiveLang()) || this.languages[0];

  ngOnInit(): void {
    this.initAuth();
    this.initUserMenu();
  }

  private initAuth(): void {
    if (environment.keycloak.enabled) {
      this.isAuthenticated = this.keycloak.isLoggedIn();
      if (this.isAuthenticated) {
        this.keycloak.loadUserProfile().then(profile => {
          this.userName = profile.firstName || profile.username || 'User';
          this.userInitials = this.getInitials(profile.firstName, profile.lastName);
        });
      }
    }
  }

  private initUserMenu(): void {
    this.userMenuItems = [
      {
        label: 'Profile',
        icon: 'pi pi-user',
        routerLink: '/profile'
      },
      {
        label: 'Settings',
        icon: 'pi pi-cog',
        routerLink: '/settings'
      },
      {
        separator: true
      },
      {
        label: 'Logout',
        icon: 'pi pi-sign-out',
        command: () => this.logout()
      }
    ];
  }

  private getInitials(firstName?: string, lastName?: string): string {
    const first = firstName?.charAt(0)?.toUpperCase() || '';
    const last = lastName?.charAt(0)?.toUpperCase() || '';
    return first + last || 'U';
  }

  onLanguageChange(lang: Language): void {
    if (lang) {
      this.translocoService.setActiveLang(lang.code);
      this.selectedLanguage = lang;
    }
  }

  logout(): void {
    if (environment.keycloak.enabled) {
      this.keycloak.logout(window.location.origin);
    } else {
      console.log('Logout clicked (Keycloak disabled)');
    }
  }

  login(): void {
    this.keycloak.login({
      redirectUri: window.location.href
    });
  }
}
