import { Component, afterNextRender, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

// PrimeNG Components
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';
import { AvatarModule } from 'primeng/avatar';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { DividerModule } from 'primeng/divider';
import { TimelineModule } from 'primeng/timeline';
import { ChipModule } from 'primeng/chip';
import { InputTextModule } from 'primeng/inputtext';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { AnimateOnScrollModule } from 'primeng/animateonscroll';
import { TranslocoModule, TranslocoService } from '@jsverse/transloco';
import { toSignal } from '@angular/core/rxjs-interop';

interface TimelineStep {
  number?: string;
  icon?: string;
  stepIcon: string;
  titleKey: string;
  descriptionKey: string;
}

interface Feature {
  icon: string;
  titleKey: string;
  descriptionKey: string;
}

@Component({
  selector: 'app-home',
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    CardModule,
    TagModule,
    AvatarModule,
    AvatarGroupModule,
    DividerModule,
    TimelineModule,
    ChipModule,
    InputTextModule,
    IconFieldModule,
    InputIconModule,
    AnimateOnScrollModule,
    TranslocoModule,
  ],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {
  private translocoService = inject(TranslocoService);
  private activeLang = toSignal(this.translocoService.langChanges$, { initialValue: this.translocoService.getActiveLang() });

  // Computed features that update when language changes
  features = computed(() => {
    const lang = this.activeLang();
    return [
      {
        icon: 'pi pi-microchip-ai',
        title: this.translocoService.translate('home.features.aiPoweredMatching'),
        description: this.translocoService.translate('home.features.aiPoweredMatchingDesc'),
      },
      {
        icon: 'pi pi-bell',
        title: this.translocoService.translate('home.features.smartAlerts'),
        description: this.translocoService.translate('home.features.smartAlertsDesc'),
      },
      {
        icon: 'pi pi-shield',
        title: this.translocoService.translate('home.features.privacyFirst'),
        description: this.translocoService.translate('home.features.privacyFirstDesc'),
      },
      {
        icon: 'pi pi-chart-line',
        title: this.translocoService.translate('home.features.applicationTracker'),
        description: this.translocoService.translate('home.features.applicationTrackerDesc'),
      },
      {
        icon: 'pi pi-file-edit',
        title: this.translocoService.translate('home.features.resumeBuilder'),
        description: this.translocoService.translate('home.features.resumeBuilderDesc'),
      },
      {
        icon: 'pi pi-comments',
        title: this.translocoService.translate('home.features.interviewPrep'),
        description: this.translocoService.translate('home.features.interviewPrepDesc'),
      },
    ];
  });

  companies: string[] = ['Google', 'Meta', 'Amazon', 'Microsoft', 'Apple'];
}
