import { Injectable, inject } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { environment } from '../../../environments/environments';

declare let gtag: Function;

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private router = inject(Router);

  init(): void {
    this.trackPageViews();
  }

  private trackPageViews(): void {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      gtag('config', environment.googleAnalyticsId, {
        page_path: event.urlAfterRedirects
      });
    });
  }

  trackEvent(eventName: string, eventParams: Record<string, any> = {}): void {
    gtag('event', eventName, eventParams);
  }
}
