import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JobFinder } from './job-finder';

describe('JobFinder', () => {
  let component: JobFinder;
  let fixture: ComponentFixture<JobFinder>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JobFinder]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JobFinder);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
