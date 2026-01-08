import { ComponentFixture, TestBed } from '@angular/core/testing';
import { JobResults } from './job-results';

describe('JobResults', () => {
  let component: JobResults;
  let fixture: ComponentFixture<JobResults>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JobResults]
    })
    .compileComponents();

    fixture = TestBed.createComponent(JobResults);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
