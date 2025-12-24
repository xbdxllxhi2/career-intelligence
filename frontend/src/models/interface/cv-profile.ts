export interface CvProfile {
  firstName?: string;
  lastName?: string;
  title?: string;                // e.g. "Java Software Engineer | DevOps"
  summary?: string;              // 2–4 lines, ATS-optimized

  yearsOfExperience?: number;

  location: {
    city?: string;
    country?: string;
    remote?: boolean;
  };

  availability?: string;        // e.g. "Immediate", "1 month notice"
  contractType?: 'Internship' | 'Full-time' | 'Part-time' | 'Freelance';

  contact: {
    email?: string;
    phone?: string;
    linkedin?: string;
    github?: string;
    portfolio?: string;
  };

  languages: Array<{
    name: string;
    level: 'Native' | 'Fluent' | 'Professional' | 'Intermediate' | 'Basic';
  }>;

  keywords?: string[];           // Explicit ATS keywords (Java, Spring Boot, Keycloak…)
}
