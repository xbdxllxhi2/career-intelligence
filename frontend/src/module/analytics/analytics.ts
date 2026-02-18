import { Component, OnInit, OnDestroy, signal, computed, effect, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

// PrimeNG Components
import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';
import { ProgressBarModule } from 'primeng/progressbar';
import { ChipModule } from 'primeng/chip';
import { TabsModule } from 'primeng/tabs';
import { DividerModule } from 'primeng/divider';
import { ButtonModule } from 'primeng/button';
import { SkeletonModule } from 'primeng/skeleton';
import { TooltipModule } from 'primeng/tooltip';
import { ChartModule } from 'primeng/chart';
import { SelectModule } from 'primeng/select';
import { SelectButtonModule } from 'primeng/selectbutton';
import { DatePickerModule } from 'primeng/datepicker';
import { TranslocoModule, TranslocoService } from '@jsverse/transloco';
import { toSignal } from '@angular/core/rxjs-interop';

import {
  AnalyticsService,
  MarketAnalysis,
  ProfileAnalysis,
  SkillGap,
  Country,
  Region,
  City,
  AnalyticsFilters,
  TimeFilter,
} from '../../service/analytics-service';

@Component({
  selector: 'app-analytics',
  imports: [
    CommonModule,
    FormsModule,
    CardModule,
    TagModule,
    ProgressBarModule,
    ChipModule,
    TabsModule,
    DividerModule,
    ButtonModule,
    SkeletonModule,
    TooltipModule,
    ChartModule,
    SelectModule,
    SelectButtonModule,
    DatePickerModule,
    TranslocoModule,
  ],
  templateUrl: './analytics.html',
  styleUrl: './analytics.scss',
})
export class Analytics implements OnInit, OnDestroy {
  private translocoService = inject(TranslocoService);
  private activeLang = toSignal(this.translocoService.langChanges$, { initialValue: this.translocoService.getActiveLang() });

  marketAnalysis = signal<MarketAnalysis | null>(null);
  profileAnalysis = signal<ProfileAnalysis | null>(null);
  isLoadingMarket = signal(true);
  isLoadingProfile = signal(true);
  activeTab = signal(0);

  // Location filters
  countries = signal<Country[]>([]);
  regions = signal<Region[]>([]);
  cities = signal<City[]>([]);
  
  selectedCountry = signal<Country | null>(null);
  selectedRegion = signal<Region | null>(null);
  selectedCity = signal<City | null>(null);

  // Time filters
  timePeriods: { label: string; value: TimeFilter['period'] }[] = [];
  selectedPeriod = signal<TimeFilter['period']>('month');
  customDateRange = signal<Date[] | null>(null);
  
  // Auto-refresh
  autoRefresh = signal(false);
  lastUpdated = signal<Date>(new Date());
  private refreshInterval: any;

  // Active filter summary
  activeFilterSummary = computed(() => {
    const parts: string[] = [];
    const country = this.selectedCountry();
    const region = this.selectedRegion();
    const city = this.selectedCity();
    
    if (city) parts.push(city.name);
    else if (region) parts.push(region.name);
    else if (country) parts.push(country.name);
    else parts.push('Tous les pays');

    const periodLabels: Record<TimeFilter['period'], string> = {
      'today': 'Aujourd\'hui',
      'week': 'Cette semaine',
      'month': 'Ce mois',
      'quarter': 'Ce trimestre',
      'year': 'Cette année',
      'custom': 'Personnalisé'
    };
    parts.push(periodLabels[this.selectedPeriod()]);

    return parts.join(' • ');
  });

  // Dynamic chart titles based on filter level
  regionChartTitle = computed(() => {
    const city = this.selectedCity();
    const region = this.selectedRegion();
    
    if (city) return `Offres par quartier - ${city.name}`;
    if (region) return `Offres par ville - ${region.name}`;
    return 'Offres d\'emploi par région';
  });

  seasonalChartTitle = computed(() => {
    const period = this.selectedPeriod();
    if (period === 'today') return 'Publications par heure';
    if (period === 'week') return 'Publications par jour';
    return 'Tendances saisonnières';
  });

  trendChartTitle = computed(() => {
    const period = this.selectedPeriod();
    if (period === 'today' || period === 'week') return 'Évolution récente du marché';
    return 'Évolution du marché (6 mois)';
  });

  // Chart configurations
  chartOptions = {
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#a3a3a3',
          font: { size: 12 }
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#a3a3a3', maxRotation: 45, minRotation: 45 },
        grid: { color: 'rgba(163, 163, 163, 0.1)' }
      },
      y: {
        ticks: { color: '#a3a3a3' },
        grid: { color: 'rgba(163, 163, 163, 0.1)' }
      }
    }
  };

  horizontalBarOptions = {
    indexAxis: 'y' as const,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      x: {
        ticks: { color: '#a3a3a3' },
        grid: { color: 'rgba(163, 163, 163, 0.1)' }
      },
      y: {
        ticks: { color: '#a3a3a3' },
        grid: { color: 'rgba(163, 163, 163, 0.1)' }
      }
    }
  };

  pieChartOptions = {
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#a3a3a3',
          font: { size: 11 },
          padding: 15
        }
      }
    }
  };

  // Computed chart data
  contractTypeChartData = computed(() => {
    const data = this.marketAnalysis();
    if (!data) return null;
    return {
      labels: data.contractTypeStats.map(c => c.type),
      datasets: [{
        data: data.contractTypeStats.map(c => c.count),
        backgroundColor: ['#10b981', '#06b6d4', '#8b5cf6', '#f59e0b', '#ef4444'],
        hoverBackgroundColor: ['#059669', '#0891b2', '#7c3aed', '#d97706', '#dc2626']
      }]
    };
  });

  jobTypeChartData = computed(() => {
    const data = this.marketAnalysis();
    if (!data) return null;
    return {
      labels: data.jobTypeStats.map(j => j.type),
      datasets: [{
        label: 'Offres',
        data: data.jobTypeStats.map(j => j.count),
        backgroundColor: 'rgba(16, 185, 129, 0.7)',
        borderColor: '#10b981',
        borderWidth: 1,
        borderRadius: 4
      }]
    };
  });

  companyChartData = computed(() => {
    const data = this.marketAnalysis();
    if (!data) return null;
    return {
      labels: data.companyStats.map(c => c.companyName),
      datasets: [{
        label: 'Postes ouverts',
        data: data.companyStats.map(c => c.openPositions),
        backgroundColor: 'rgba(139, 92, 246, 0.7)',
        borderColor: '#8b5cf6',
        borderWidth: 1,
        borderRadius: 4
      }]
    };
  });

  regionChartData = computed(() => {
    const data = this.marketAnalysis();
    if (!data) return null;
    return {
      labels: data.regionStats.map(r => r.region),
      datasets: [{
        label: 'Offres',
        data: data.regionStats.map(r => r.count),
        backgroundColor: 'rgba(6, 182, 212, 0.7)',
        borderColor: '#06b6d4',
        borderWidth: 1,
        borderRadius: 4
      }]
    };
  });

  seasonalTrendChartData = computed(() => {
    const data = this.marketAnalysis();
    if (!data) return null;
    return {
      labels: data.seasonalTrends.map(s => s.month),
      datasets: [{
        label: 'Offres publiées',
        data: data.seasonalTrends.map(s => s.jobCount),
        fill: true,
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderColor: '#10b981',
        tension: 0.4,
        pointBackgroundColor: '#10b981',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#10b981'
      }]
    };
  });

  monthlyTrendChartData = computed(() => {
    const data = this.marketAnalysis();
    if (!data) return null;
    return {
      labels: data.monthlyJobTrends.map(m => m.month),
      datasets: [{
        label: 'Total offres actives',
        data: data.monthlyJobTrends.map(m => m.count),
        fill: true,
        backgroundColor: 'rgba(139, 92, 246, 0.2)',
        borderColor: '#8b5cf6',
        tension: 0.4,
        pointBackgroundColor: '#8b5cf6',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#8b5cf6'
      }]
    };
  });

  constructor(private analyticsService: AnalyticsService) {
    // Watch for auto-refresh toggle
    effect(() => {
      if (this.autoRefresh()) {
        this.startAutoRefresh();
      } else {
        this.stopAutoRefresh();
      }
    });
  }

  ngOnInit(): void {
    this.timePeriods = this.analyticsService.getTimePeriods();
    this.loadCountries();
    this.loadMarketAnalysis();
    this.loadProfileAnalysis();
  }

  ngOnDestroy(): void {
    this.stopAutoRefresh();
  }

  // Location filter methods
  loadCountries(): void {
    this.analyticsService.getCountries().subscribe(countries => {
      this.countries.set(countries);
    });
  }

  onCountryChange(country: Country | null): void {
    this.selectedCountry.set(country);
    this.selectedRegion.set(null);
    this.selectedCity.set(null);
    this.regions.set([]);
    this.cities.set([]);
    
    if (country) {
      this.analyticsService.getRegions(country.code).subscribe(regions => {
        this.regions.set(regions);
      });
    }
    this.applyFilters();
  }

  onRegionChange(region: Region | null): void {
    this.selectedRegion.set(region);
    this.selectedCity.set(null);
    this.cities.set([]);
    
    if (region) {
      this.analyticsService.getCities(region.code).subscribe(cities => {
        this.cities.set(cities);
      });
    }
    this.applyFilters();
  }

  onCityChange(city: City | null): void {
    this.selectedCity.set(city);
    this.applyFilters();
  }

  onPeriodChange(period: TimeFilter['period']): void {
    this.selectedPeriod.set(period);
    this.applyFilters();
  }

  onDateRangeChange(range: Date[] | null): void {
    this.customDateRange.set(range);
    if (range && range.length === 2) {
      this.applyFilters();
    }
  }

  clearFilters(): void {
    this.selectedCountry.set(null);
    this.selectedRegion.set(null);
    this.selectedCity.set(null);
    this.selectedPeriod.set('month');
    this.customDateRange.set(null);
    this.regions.set([]);
    this.cities.set([]);
    this.applyFilters();
  }

  refreshData(): void {
    this.lastUpdated.set(new Date());
    this.applyFilters();
  }

  private startAutoRefresh(): void {
    this.refreshInterval = setInterval(() => {
      this.refreshData();
    }, 30000); // Refresh every 30 seconds
  }

  private stopAutoRefresh(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }

  private buildFilters(): AnalyticsFilters {
    return {
      location: {
        country: this.selectedCountry()?.code,
        region: this.selectedRegion()?.code,
        city: this.selectedCity()?.code,
      },
      time: {
        period: this.selectedPeriod(),
        startDate: this.customDateRange()?.[0],
        endDate: this.customDateRange()?.[1],
      }
    };
  }

  private applyFilters(): void {
    this.loadMarketAnalysis();
  }

  loadMarketAnalysis(): void {
    this.isLoadingMarket.set(true);
    const filters = this.buildFilters();
    this.analyticsService.getMarketAnalysis(filters).subscribe({
      next: (data) => {
        this.marketAnalysis.set(data);
        this.isLoadingMarket.set(false);
        this.lastUpdated.set(new Date());
      },
      error: () => {
        this.isLoadingMarket.set(false);
      },
    });
  }

  loadProfileAnalysis(): void {
    this.isLoadingProfile.set(true);
    this.analyticsService.getProfileAnalysis().subscribe({
      next: (data) => {
        this.profileAnalysis.set(data);
        this.isLoadingProfile.set(false);
      },
      error: () => {
        this.isLoadingProfile.set(false);
      },
    });
  }

  getScoreColor(score: number): string {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-amber-400';
    return 'text-rose-400';
  }

  getScoreSeverity(score: number): 'success' | 'warn' | 'danger' {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warn';
    return 'danger';
  }

  getPriorityColor(priority: string): 'danger' | 'warn' | 'info' {
    switch (priority) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'warn';
      default:
        return 'info';
    }
  }

  getTrendIcon(trend: string): string {
    switch (trend) {
      case 'up':
        return 'pi pi-arrow-up';
      case 'down':
        return 'pi pi-arrow-down';
      default:
        return 'pi pi-minus';
    }
  }

  getTrendColor(trend: string): string {
    switch (trend) {
      case 'up':
        return 'text-emerald-400';
      case 'down':
        return 'text-rose-400';
      default:
        return 'text-neutral-400';
    }
  }

  getGrowthPotentialColor(potential: string): 'success' | 'warn' | 'secondary' {
    switch (potential) {
      case 'high':
        return 'success';
      case 'medium':
        return 'warn';
      default:
        return 'secondary';
    }
  }

  calculateGapPercentage(gap: SkillGap): number {
    return Math.max(0, gap.marketDemand - gap.userLevel);
  }

  onTabChange(event: string | number | undefined): void {
    if (typeof event === 'number') {
      this.activeTab.set(event);
    }
  }

  formatSalary(salary: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0,
    }).format(salary);
  }
}
