import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DrawerModule } from 'primeng/drawer';
import { ButtonModule } from 'primeng/button';
import { BadgeModule } from 'primeng/badge';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { SelectModule } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { TranslocoService, TranslocoModule } from '@jsverse/transloco';

interface Language {
  code: string;
  name: string;
  flag: string;
}

@Component({
  selector: 'app-sidebar',
  imports: [CommonModule, DrawerModule, ButtonModule, BadgeModule, RouterLink, RouterLinkActive, SelectModule, FormsModule, TranslocoModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class Sidebar {
  private translocoService = inject(TranslocoService);
  
  visible = false;

  languages: Language[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' }
  ];

  selectedLanguage: Language = this.languages.find(l => l.code === this.translocoService.getActiveLang()) || this.languages[0];

  onLanguageChange(lang: Language): void {
    if (lang) {
      this.translocoService.setActiveLang(lang.code);
      this.selectedLanguage = lang;
    }
  }

  logout(): void {
    // TODO: Implement logout logic
    console.log('Logout clicked');
  }
}
