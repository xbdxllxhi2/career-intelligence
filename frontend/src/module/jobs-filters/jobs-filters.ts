import { Component, EventEmitter, inject, Input, OnInit, Output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AccordionModule } from 'primeng/accordion';
import { FloatLabelModule } from 'primeng/floatlabel';
import { ButtonModule } from 'primeng/button';
import { CommonModule } from '@angular/common';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { CheckboxModule } from 'primeng/checkbox';
import { ToggleSwitchModule } from 'primeng/toggleswitch';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { ChipModule } from 'primeng/chip';
import { TooltipModule } from 'primeng/tooltip';
import { TranslocoModule } from '@jsverse/transloco';
import { JobFilters } from '../../models/filters/job-filters';
import { FilterOptions } from '../../models/filters/filter-options';
import { JobService } from '../../service/job-service';

interface SelectOption {
  label: string;
  value: string;
}

@Component({
  selector: 'app-jobs-filters',
  imports: [
    FormsModule,
    AccordionModule,
    FloatLabelModule,
    ButtonModule,
    CommonModule,
    InputTextModule,
    SelectModule,
    CheckboxModule,
    ToggleSwitchModule,
    AutoCompleteModule,
    ChipModule,
    TooltipModule,
    TranslocoModule,
  ],
  templateUrl: './jobs-filters.html',
  styleUrl: './jobs-filters.scss',
})
export class JobsFilters implements OnInit {
  private jobService = inject(JobService);

  @Input() sideFilterActive = false;
  @Input({ required: true }) totalSearchResults = 0;

  @Output() searchEvent = new EventEmitter<JobFilters>();
  @Output() smartSearchEvent = new EventEmitter<void>();

  filters: JobFilters = {};

  // Filter options
  countryOptions = signal<SelectOption[]>([]);
  regionOptions = signal<SelectOption[]>([]);
  cityOptions = signal<SelectOption[]>([]);
  seniorityOptions = signal<SelectOption[]>([]);
  sourceOptions = signal<SelectOption[]>([]);

  // Filtered options for autocomplete
  filteredCities = signal<SelectOption[]>([]);
  filteredRegions = signal<SelectOption[]>([]);

  // Selected values (can be SelectOption object or string from autocomplete input)
  selectedCountry: SelectOption | null = null;
  selectedRegion: SelectOption | string | null = null;
  selectedCity: SelectOption | string | null = null;
  selectedSeniority: SelectOption | null = null;
  selectedSource: SelectOption | null = null;
  includeExpired = false;
  hasEasyApply = false;

  ngOnInit(): void {
    this.loadFilterOptions();
  }

  private loadFilterOptions(): void {
    this.jobService.getFilterOptions().subscribe({
      next: (options: FilterOptions) => {
        this.countryOptions.set(this.mapToSelectOptions(options.countries));
        this.regionOptions.set(this.mapToSelectOptions(options.regions));
        this.cityOptions.set(this.mapToSelectOptions(options.cities));
        this.seniorityOptions.set(this.mapToSelectOptions(options.seniority_levels));
        this.sourceOptions.set(this.mapToSelectOptions(options.sources));

        this.filteredCities.set(this.cityOptions());
        this.filteredRegions.set(this.regionOptions());
      },
      error: (err) => console.error('Failed to load filter options', err),
    });
  }

  private mapToSelectOptions(values: string[]): SelectOption[] {
    return values.map((v) => ({ label: v, value: v }));
  }

  filterCities(event: { query: string }): void {
    const query = event.query.toLowerCase();
    this.filteredCities.set(
      this.cityOptions().filter((c) => c.label.toLowerCase().includes(query))
    );
  }

  filterRegions(event: { query: string }): void {
    const query = event.query.toLowerCase();
    this.filteredRegions.set(
      this.regionOptions().filter((r) => r.label.toLowerCase().includes(query))
    );
  }

  emitSearchEvent(): void {
    this.filters = {
      ...this.filters,
      country: this.getFilterValue(this.selectedCountry),
      region: this.getFilterValue(this.selectedRegion),
      city: this.getFilterValue(this.selectedCity),
      seniority: this.getFilterValue(this.selectedSeniority),
      source: this.getFilterValue(this.selectedSource),
      include_expired: this.includeExpired,
      has_easy_apply: this.hasEasyApply || undefined,
    };
    this.searchEvent.emit(this.filters);
  }

  private getFilterValue(selected: SelectOption | string | null | undefined): string | undefined {
    if (!selected) return undefined;
    if (typeof selected === 'string') return selected;
    return selected.value;
  }

  getFilterLabel(selected: SelectOption | string | null | undefined): string {
    if (!selected) return '';
    if (typeof selected === 'string') return selected;
    return selected.label;
  }

  clearFilters(): void {
    this.filters = {};
    this.selectedCountry = null;
    this.selectedRegion = null;
    this.selectedCity = null;
    this.selectedSeniority = null;
    this.selectedSource = null;
    this.includeExpired = false;
    this.hasEasyApply = false;
    this.searchEvent.emit(this.filters);
  }

  emitSmartSearchEvent(): void {
    this.smartSearchEvent.emit();
  }

  getActiveFilterCount(): number {
    let count = 0;
    if (this.filters.title_contains) count++;
    if (this.filters.description_contains) count++;
    if (this.getFilterValue(this.selectedCountry)) count++;
    if (this.getFilterValue(this.selectedRegion)) count++;
    if (this.getFilterValue(this.selectedCity)) count++;
    if (this.getFilterValue(this.selectedSeniority)) count++;
    if (this.getFilterValue(this.selectedSource)) count++;
    if (this.includeExpired) count++;
    if (this.hasEasyApply) count++;
    return count;
  }
}
