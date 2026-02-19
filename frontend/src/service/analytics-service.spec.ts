import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { AnalyticsService } from './analytics-service';

describe('AnalyticsService', () => {
  let service: AnalyticsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AnalyticsService],
    });
    service = TestBed.inject(AnalyticsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return market analysis data', (done) => {
    service.getMarketAnalysis().subscribe((data) => {
      expect(data).toBeTruthy();
      expect(data.totalActiveJobs).toBeGreaterThan(0);
      expect(data.marketTrends.length).toBeGreaterThan(0);
      done();
    });
  });

  it('should return profile analysis data', (done) => {
    service.getProfileAnalysis().subscribe((data) => {
      expect(data).toBeTruthy();
      expect(data.overallScore).toBeGreaterThanOrEqual(0);
      expect(data.skillGaps.length).toBeGreaterThan(0);
      done();
    });
  });
});
