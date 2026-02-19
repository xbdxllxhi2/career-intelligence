import { Component, inject, computed, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DrawerModule } from 'primeng/drawer';
import { ButtonModule } from 'primeng/button';
import { MenuModule } from 'primeng/menu';
import { BadgeModule } from 'primeng/badge';
import { MenuItem } from 'primeng/api';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { SelectModule } from 'primeng/select';
import { FormsModule } from '@angular/forms';
import { TranslocoService, TranslocoModule, translate } from '@jsverse/transloco';
import { toSignal } from '@angular/core/rxjs-interop';

interface Language {
  code: string;
  name: string;
  flag: string;
}

@Component({
  selector: 'app-sidebar',
  imports: [CommonModule, DrawerModule, ButtonModule, MenuModule, BadgeModule, RouterLink, RouterLinkActive, SelectModule, FormsModule, TranslocoModule],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class Sidebar {
  private translocoService = inject(TranslocoService);
  
  visible = false;
  active: string = '';

  languages: Language[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' }
  ];

  selectedLanguage: Language = this.languages.find(l => l.code === this.translocoService.getActiveLang()) || this.languages[0];

  // Track language changes
  private activeLang = toSignal(this.translocoService.langChanges$, { initialValue: this.translocoService.getActiveLang() });

  // Computed menu items that update when language changes
  items = computed<MenuItem[]>(() => {
    const lang = this.activeLang();
    return [
      {
        label: this.translocoService.translate('nav.home'),
        icon: 'pi pi-home',
        routerLink: ['/'],
        routerLinkActiveOptions: { exact: true },
      },
      { label: this.translocoService.translate('nav.profile'), icon: 'pi pi-user', routerLink: ['/profile'] },
      { label: this.translocoService.translate('nav.jobs'), icon: 'pi pi-code', routerLink: ['/jobs'] },
      { label: this.translocoService.translate('nav.applications'), icon: 'pi pi-briefcase', routerLink: ['/applications'] },
      { label: this.translocoService.translate('nav.analytics'), icon: 'pi pi-chart-line', routerLink: ['/analytics'] },
      { label: this.translocoService.translate('nav.messages'), icon: 'pi pi-inbox', routerLink: ['/messages'] },
      { label: this.translocoService.translate('nav.resume'), icon: 'pi pi-file-edit', routerLink: ['/resume'] },
    ];
  });

  items2 = computed<MenuItem[]>(() => {
    const lang = this.activeLang();
    return [
      { label: this.translocoService.translate('nav.logout'), icon: 'pi pi-sign-out', routerLink: ['/logout'] },
      { label: this.translocoService.translate('nav.settings'), icon: 'pi pi-cog', routerLink: ['/settings'] },
      { label: this.translocoService.translate('nav.contact'), icon: 'pi pi-envelope', routerLink: ['/contact'] },
    ];
  });

  onLanguageChange(lang: Language): void {
    if (lang) {
      this.translocoService.setActiveLang(lang.code);
      this.selectedLanguage = lang;
    }
  }
}
