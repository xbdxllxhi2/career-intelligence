import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environments';
import { Observable, of, delay } from 'rxjs';

// Location interfaces
export interface Country {
  code: string;
  name: string;
}

export interface Region {
  code: string;
  name: string;
  countryCode: string;
}

export interface City {
  code: string;
  name: string;
  regionCode: string;
}

export interface LocationFilter {
  country?: string;
  region?: string;
  city?: string;
}

export interface TimeFilter {
  period: 'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom';
  startDate?: Date;
  endDate?: Date;
}

export interface AnalyticsFilters {
  location: LocationFilter;
  time: TimeFilter;
}

export interface MarketTrend {
  skill: string;
  demandGrowth: number;
  avgSalary: number;
  openPositions: number;
}

export interface CompanyHiringStats {
  companyName: string;
  openPositions: number;
  avgMatchScore: number;
  topSkills: string[];
}

export interface SkillDemand {
  skill: string;
  demand: number;
  trend: 'up' | 'down' | 'stable';
  category: string;
}

export interface ContractTypeStats {
  type: string;
  count: number;
  percentage: number;
}

export interface JobTypeStats {
  type: string;
  count: number;
}

export interface RegionStats {
  region: string;
  count: number;
  avgSalary: number;
}

export interface SeasonalTrend {
  month: string;
  jobCount: number;
  year: number;
}

export interface MarketAnalysis {
  totalActiveJobs: number;
  newJobsThisWeek: number;
  avgSalary: number;
  topGrowingSectors: string[];
  marketTrends: MarketTrend[];
  companyStats: CompanyHiringStats[];
  skillDemands: SkillDemand[];
  contractTypeStats: ContractTypeStats[];
  jobTypeStats: JobTypeStats[];
  regionStats: RegionStats[];
  seasonalTrends: SeasonalTrend[];
  monthlyJobTrends: { month: string; count: number }[];
}

export interface SkillGap {
  skill: string;
  userLevel: number;
  marketDemand: number;
  priority: 'high' | 'medium' | 'low';
  recommendation: string;
}

export interface ProfileStrength {
  category: string;
  score: number;
  tips: string[];
}

export interface CareerRecommendation {
  title: string;
  matchScore: number;
  requiredSkills: string[];
  estimatedSalaryRange: string;
  growthPotential: 'high' | 'medium' | 'low';
}

export interface ProfileAnalysis {
  overallScore: number;
  marketFitScore: number;
  profileStrengths: ProfileStrength[];
  skillGaps: SkillGap[];
  topMatchingJobs: number;
  careerRecommendations: CareerRecommendation[];
  improvementAreas: string[];
}

@Injectable({
  providedIn: 'root',
})
export class AnalyticsService {
  private readonly apiUrl = environment.apiUrl + '/analytics';

  constructor(private client: HttpClient) {}

  // Location data
  getCountries(): Observable<Country[]> {
    return of([
      { code: 'FR', name: 'France' },
      { code: 'BE', name: 'Belgique' },
      { code: 'CH', name: 'Suisse' },
      { code: 'CA', name: 'Canada' },
      { code: 'LU', name: 'Luxembourg' },
    ]).pipe(delay(200));
  }

  getRegions(countryCode: string): Observable<Region[]> {
    const regionsByCountry: Record<string, Region[]> = {
      'FR': [
        { code: 'IDF', name: 'Île-de-France', countryCode: 'FR' },
        { code: 'ARA', name: 'Auvergne-Rhône-Alpes', countryCode: 'FR' },
        { code: 'PACA', name: 'Provence-Alpes-Côte d\'Azur', countryCode: 'FR' },
        { code: 'OCC', name: 'Occitanie', countryCode: 'FR' },
        { code: 'NAQ', name: 'Nouvelle-Aquitaine', countryCode: 'FR' },
        { code: 'PDL', name: 'Pays de la Loire', countryCode: 'FR' },
        { code: 'BRE', name: 'Bretagne', countryCode: 'FR' },
        { code: 'GES', name: 'Grand Est', countryCode: 'FR' },
        { code: 'HDF', name: 'Hauts-de-France', countryCode: 'FR' },
        { code: 'NOR', name: 'Normandie', countryCode: 'FR' },
      ],
      'BE': [
        { code: 'BRU', name: 'Bruxelles-Capitale', countryCode: 'BE' },
        { code: 'WAL', name: 'Wallonie', countryCode: 'BE' },
        { code: 'VLA', name: 'Flandre', countryCode: 'BE' },
      ],
      'CH': [
        { code: 'GE', name: 'Genève', countryCode: 'CH' },
        { code: 'VD', name: 'Vaud', countryCode: 'CH' },
        { code: 'ZH', name: 'Zürich', countryCode: 'CH' },
      ],
      'CA': [
        { code: 'QC', name: 'Québec', countryCode: 'CA' },
        { code: 'ON', name: 'Ontario', countryCode: 'CA' },
        { code: 'BC', name: 'Colombie-Britannique', countryCode: 'CA' },
      ],
      'LU': [
        { code: 'LUX', name: 'Luxembourg', countryCode: 'LU' },
      ],
    };
    return of(regionsByCountry[countryCode] || []).pipe(delay(200));
  }

  getCities(regionCode: string): Observable<City[]> {
    const citiesByRegion: Record<string, City[]> = {
      'IDF': [
        { code: 'PAR', name: 'Paris', regionCode: 'IDF' },
        { code: 'LDE', name: 'La Défense', regionCode: 'IDF' },
        { code: 'BOL', name: 'Boulogne-Billancourt', regionCode: 'IDF' },
        { code: 'VER', name: 'Versailles', regionCode: 'IDF' },
        { code: 'NAN', name: 'Nanterre', regionCode: 'IDF' },
      ],
      'ARA': [
        { code: 'LYO', name: 'Lyon', regionCode: 'ARA' },
        { code: 'GRE', name: 'Grenoble', regionCode: 'ARA' },
        { code: 'STE', name: 'Saint-Étienne', regionCode: 'ARA' },
      ],
      'PACA': [
        { code: 'MAR', name: 'Marseille', regionCode: 'PACA' },
        { code: 'NIC', name: 'Nice', regionCode: 'PACA' },
        { code: 'AIX', name: 'Aix-en-Provence', regionCode: 'PACA' },
      ],
      'OCC': [
        { code: 'TLS', name: 'Toulouse', regionCode: 'OCC' },
        { code: 'MTP', name: 'Montpellier', regionCode: 'OCC' },
      ],
      'BRU': [
        { code: 'BXL', name: 'Bruxelles', regionCode: 'BRU' },
      ],
      'QC': [
        { code: 'MTL', name: 'Montréal', regionCode: 'QC' },
        { code: 'QUE', name: 'Québec City', regionCode: 'QC' },
      ],
      'GE': [
        { code: 'GEN', name: 'Genève', regionCode: 'GE' },
      ],
    };
    return of(citiesByRegion[regionCode] || []).pipe(delay(200));
  }

  // Time period options
  getTimePeriods(): { label: string; value: TimeFilter['period'] }[] {
    return [
      { label: 'Aujourd\'hui', value: 'today' },
      { label: 'Cette semaine', value: 'week' },
      { label: 'Ce mois', value: 'month' },
      { label: 'Ce trimestre', value: 'quarter' },
      { label: 'Cette année', value: 'year' },
      { label: 'Personnalisé', value: 'custom' },
    ];
  }

  // Market analysis with filters
  getMarketAnalysis(filters?: AnalyticsFilters): Observable<MarketAnalysis> {
    // In real implementation, filters would be sent to backend
    // Here we simulate different data based on filters
    const multiplier = this.getMultiplierFromFilters(filters);
    const locationLabel = this.getLocationLabel(filters);

    const dummyData: MarketAnalysis = {
      totalActiveJobs: Math.round(15420 * multiplier),
      newJobsThisWeek: Math.round(1234 * multiplier),
      avgSalary: Math.round(55000 * (0.8 + multiplier * 0.4)),
      topGrowingSectors: ['Tech', 'Healthcare', 'Finance', 'E-commerce'],
      marketTrends: [
        { skill: 'Python', demandGrowth: 25 + Math.round(Math.random() * 5), avgSalary: 65000, openPositions: Math.round(3200 * multiplier) },
        { skill: 'React', demandGrowth: 22 + Math.round(Math.random() * 5), avgSalary: 62000, openPositions: Math.round(2800 * multiplier) },
        { skill: 'Data Science', demandGrowth: 30 + Math.round(Math.random() * 5), avgSalary: 72000, openPositions: Math.round(1500 * multiplier) },
        { skill: 'Cloud (AWS/GCP)', demandGrowth: 28 + Math.round(Math.random() * 5), avgSalary: 70000, openPositions: Math.round(2100 * multiplier) },
        { skill: 'DevOps', demandGrowth: 20 + Math.round(Math.random() * 5), avgSalary: 68000, openPositions: Math.round(1800 * multiplier) },
      ],
      companyStats: [
        { companyName: 'TechCorp', openPositions: Math.round(45 * multiplier), avgMatchScore: 87, topSkills: ['React', 'Node.js', 'AWS'] },
        { companyName: 'DataFlow Inc', openPositions: Math.round(32 * multiplier), avgMatchScore: 82, topSkills: ['Python', 'ML', 'SQL'] },
        { companyName: 'CloudFirst', openPositions: Math.round(28 * multiplier), avgMatchScore: 79, topSkills: ['Kubernetes', 'Docker', 'Terraform'] },
        { companyName: 'FinTech Solutions', openPositions: Math.round(25 * multiplier), avgMatchScore: 75, topSkills: ['Java', 'Spring', 'Microservices'] },
      ],
      skillDemands: [
        { skill: 'JavaScript', demand: 95, trend: 'stable', category: 'Programming' },
        { skill: 'Python', demand: 92, trend: 'up', category: 'Programming' },
        { skill: 'React', demand: 88, trend: 'up', category: 'Frontend' },
        { skill: 'AWS', demand: 85, trend: 'up', category: 'Cloud' },
        { skill: 'Docker', demand: 82, trend: 'up', category: 'DevOps' },
        { skill: 'SQL', demand: 80, trend: 'stable', category: 'Database' },
        { skill: 'TypeScript', demand: 78, trend: 'up', category: 'Programming' },
        { skill: 'Kubernetes', demand: 75, trend: 'up', category: 'DevOps' },
      ],
      contractTypeStats: [
        { type: 'CDI', count: Math.round(6500 * multiplier), percentage: 42 },
        { type: 'CDD', count: Math.round(3200 * multiplier), percentage: 21 },
        { type: 'Stage', count: Math.round(2800 * multiplier), percentage: 18 },
        { type: 'Alternance', count: Math.round(1900 * multiplier), percentage: 12 },
        { type: 'Freelance', count: Math.round(1020 * multiplier), percentage: 7 },
      ],
      jobTypeStats: [
        { type: 'Développeur Full Stack', count: Math.round(2800 * multiplier) },
        { type: 'Data Scientist', count: Math.round(1950 * multiplier) },
        { type: 'DevOps Engineer', count: Math.round(1720 * multiplier) },
        { type: 'Frontend Developer', count: Math.round(1540 * multiplier) },
        { type: 'Backend Developer', count: Math.round(1380 * multiplier) },
        { type: 'Cloud Architect', count: Math.round(980 * multiplier) },
        { type: 'Product Manager', count: Math.round(850 * multiplier) },
        { type: 'UX Designer', count: Math.round(720 * multiplier) },
      ],
      regionStats: this.getRegionStatsForFilters(filters, multiplier),
      seasonalTrends: this.getSeasonalTrendsForFilters(filters, multiplier),
      monthlyJobTrends: this.getMonthlyTrendsForFilters(filters, multiplier),
    };

    return of(dummyData).pipe(delay(500));
  }

  private getMultiplierFromFilters(filters?: AnalyticsFilters): number {
    if (!filters) return 1;
    
    // Simulate different data volumes based on location scope
    if (filters.location.city) return 0.1;
    if (filters.location.region) return 0.3;
    if (filters.location.country) return 0.8;
    return 1;
  }

  private getLocationLabel(filters?: AnalyticsFilters): string {
    if (!filters) return 'Global';
    if (filters.location.city) return filters.location.city;
    if (filters.location.region) return filters.location.region;
    if (filters.location.country) return filters.location.country;
    return 'Global';
  }

  private getRegionStatsForFilters(filters: AnalyticsFilters | undefined, multiplier: number): RegionStats[] {
    // If city is selected, show districts/neighborhoods
    if (filters?.location.city) {
      return [
        { region: 'Centre-ville', count: Math.round(520 * multiplier), avgSalary: 58000 },
        { region: 'Zone d\'affaires', count: Math.round(410 * multiplier), avgSalary: 62000 },
        { region: 'Périphérie Nord', count: Math.round(280 * multiplier), avgSalary: 48000 },
        { region: 'Périphérie Sud', count: Math.round(220 * multiplier), avgSalary: 46000 },
        { region: 'Zone industrielle', count: Math.round(190 * multiplier), avgSalary: 44000 },
      ];
    }
    
    // If region is selected, show cities
    if (filters?.location.region) {
      return [
        { region: 'Capitale régionale', count: Math.round(2500 * multiplier), avgSalary: 52000 },
        { region: 'Ville 2', count: Math.round(1200 * multiplier), avgSalary: 48000 },
        { region: 'Ville 3', count: Math.round(800 * multiplier), avgSalary: 45000 },
        { region: 'Ville 4', count: Math.round(450 * multiplier), avgSalary: 43000 },
        { region: 'Autres', count: Math.round(250 * multiplier), avgSalary: 42000 },
      ];
    }

    // Default: show regions
    return [
      { region: 'Île-de-France', count: Math.round(5200 * multiplier), avgSalary: 58000 },
      { region: 'Auvergne-Rhône-Alpes', count: Math.round(2100 * multiplier), avgSalary: 48000 },
      { region: 'Provence-Alpes-Côte d\'Azur', count: Math.round(1450 * multiplier), avgSalary: 46000 },
      { region: 'Occitanie', count: Math.round(1200 * multiplier), avgSalary: 45000 },
      { region: 'Nouvelle-Aquitaine', count: Math.round(980 * multiplier), avgSalary: 44000 },
      { region: 'Pays de la Loire', count: Math.round(850 * multiplier), avgSalary: 43000 },
      { region: 'Bretagne', count: Math.round(720 * multiplier), avgSalary: 42000 },
      { region: 'Grand Est', count: Math.round(680 * multiplier), avgSalary: 43000 },
    ];
  }

  private getSeasonalTrendsForFilters(filters: AnalyticsFilters | undefined, multiplier: number): SeasonalTrend[] {
    const baseData = [
      { month: 'Jan', jobCount: 1200, year: 2026 },
      { month: 'Fév', jobCount: 1450, year: 2026 },
      { month: 'Mar', jobCount: 1800, year: 2026 },
      { month: 'Avr', jobCount: 2100, year: 2026 },
      { month: 'Mai', jobCount: 1950, year: 2026 },
      { month: 'Juin', jobCount: 1700, year: 2026 },
      { month: 'Juil', jobCount: 1100, year: 2026 },
      { month: 'Août', jobCount: 850, year: 2026 },
      { month: 'Sep', jobCount: 2200, year: 2026 },
      { month: 'Oct', jobCount: 2400, year: 2026 },
      { month: 'Nov', jobCount: 2100, year: 2026 },
      { month: 'Déc', jobCount: 1300, year: 2026 },
    ];

    // For daily view (today/week), show hours or days
    if (filters?.time.period === 'today') {
      return [
        { month: '08h', jobCount: Math.round(45 * multiplier), year: 2026 },
        { month: '10h', jobCount: Math.round(120 * multiplier), year: 2026 },
        { month: '12h', jobCount: Math.round(85 * multiplier), year: 2026 },
        { month: '14h', jobCount: Math.round(150 * multiplier), year: 2026 },
        { month: '16h', jobCount: Math.round(95 * multiplier), year: 2026 },
        { month: '18h', jobCount: Math.round(35 * multiplier), year: 2026 },
      ];
    }

    if (filters?.time.period === 'week') {
      return [
        { month: 'Lun', jobCount: Math.round(280 * multiplier), year: 2026 },
        { month: 'Mar', jobCount: Math.round(320 * multiplier), year: 2026 },
        { month: 'Mer', jobCount: Math.round(290 * multiplier), year: 2026 },
        { month: 'Jeu', jobCount: Math.round(310 * multiplier), year: 2026 },
        { month: 'Ven', jobCount: Math.round(250 * multiplier), year: 2026 },
        { month: 'Sam', jobCount: Math.round(45 * multiplier), year: 2026 },
        { month: 'Dim', jobCount: Math.round(15 * multiplier), year: 2026 },
      ];
    }

    return baseData.map(d => ({ ...d, jobCount: Math.round(d.jobCount * multiplier) }));
  }

  private getMonthlyTrendsForFilters(filters: AnalyticsFilters | undefined, multiplier: number): { month: string; count: number }[] {
    if (filters?.time.period === 'today' || filters?.time.period === 'week') {
      return [
        { month: 'Il y a 7j', count: Math.round(14200 * multiplier) },
        { month: 'Il y a 6j', count: Math.round(14350 * multiplier) },
        { month: 'Il y a 5j', count: Math.round(14500 * multiplier) },
        { month: 'Il y a 4j', count: Math.round(14800 * multiplier) },
        { month: 'Il y a 3j', count: Math.round(15100 * multiplier) },
        { month: 'Il y a 2j', count: Math.round(15250 * multiplier) },
        { month: 'Hier', count: Math.round(15350 * multiplier) },
        { month: 'Aujourd\'hui', count: Math.round(15420 * multiplier) },
      ];
    }

    return [
      { month: 'Sep 2025', count: Math.round(12500 * multiplier) },
      { month: 'Oct 2025', count: Math.round(13200 * multiplier) },
      { month: 'Nov 2025', count: Math.round(12800 * multiplier) },
      { month: 'Déc 2025', count: Math.round(11000 * multiplier) },
      { month: 'Jan 2026', count: Math.round(13500 * multiplier) },
      { month: 'Fév 2026', count: Math.round(15420 * multiplier) },
    ];
  }

  // Dummy data for profile analysis
  getProfileAnalysis(): Observable<ProfileAnalysis> {
    const dummyData: ProfileAnalysis = {
      overallScore: 78,
      marketFitScore: 72,
      profileStrengths: [
        { category: 'Technical Skills', score: 85, tips: ['Add more cloud certifications', 'Highlight recent projects'] },
        { category: 'Experience', score: 70, tips: ['Add measurable achievements', 'Include internship details'] },
        { category: 'Education', score: 90, tips: ['Add relevant coursework'] },
        { category: 'Soft Skills', score: 65, tips: ['Add leadership examples', 'Mention team collaboration'] },
      ],
      skillGaps: [
        { skill: 'Docker', userLevel: 30, marketDemand: 82, priority: 'high', recommendation: 'Complete Docker fundamentals course' },
        { skill: 'AWS', userLevel: 40, marketDemand: 85, priority: 'high', recommendation: 'Get AWS Cloud Practitioner certification' },
        { skill: 'Kubernetes', userLevel: 20, marketDemand: 75, priority: 'medium', recommendation: 'Learn container orchestration basics' },
        { skill: 'CI/CD', userLevel: 35, marketDemand: 70, priority: 'medium', recommendation: 'Practice with GitHub Actions or Jenkins' },
      ],
      topMatchingJobs: 156,
      careerRecommendations: [
        { title: 'Full Stack Developer', matchScore: 85, requiredSkills: ['React', 'Node.js', 'SQL'], estimatedSalaryRange: '50k - 70k €', growthPotential: 'high' },
        { title: 'Frontend Engineer', matchScore: 82, requiredSkills: ['React', 'TypeScript', 'CSS'], estimatedSalaryRange: '45k - 65k €', growthPotential: 'high' },
        { title: 'Software Engineer', matchScore: 78, requiredSkills: ['Python', 'Java', 'SQL'], estimatedSalaryRange: '48k - 68k €', growthPotential: 'medium' },
      ],
      improvementAreas: [
        'Add cloud platform experience (AWS/GCP/Azure)',
        'Include DevOps and CI/CD skills',
        'Add portfolio links or GitHub profile',
        'Get certifications in high-demand technologies',
      ],
    };

    // Simulate API delay
    return of(dummyData).pipe(delay(600));
  }

  // These methods will call the real API once backend is implemented
  // getMarketAnalysis(): Observable<MarketAnalysis> {
  //   return this.client.get<MarketAnalysis>(`${this.apiUrl}/market`);
  // }

  // getProfileAnalysis(): Observable<ProfileAnalysis> {
  //   return this.client.get<ProfileAnalysis>(`${this.apiUrl}/profile`);
  // }
}
