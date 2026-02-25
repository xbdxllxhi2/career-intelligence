import { Component, signal, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { Sidebar } from "../shared/sidebar/sidebar";
import { AnalyticsService } from './core/services/analytics.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ButtonModule, Sidebar],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('frontend');
  
  private analytics = inject(AnalyticsService);

  constructor() {
    this.analytics.init();
  }
}
