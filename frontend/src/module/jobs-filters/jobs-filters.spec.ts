import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JobsFilters } from './jobs-filters';

describe('JobsFilters', () => {
  let component: JobsFilters;
  let fixture: ComponentFixture<JobsFilters>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JobsFilters]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JobsFilters);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
