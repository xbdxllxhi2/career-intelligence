export interface UserProfile {
  firstName?: string;
  lastName?: string;
  phone?: string;
  city?: string;
  country?: string;
  email?: string;
  linkedin?: string;
  github?: string;
  summary?: string;

  education?: EducationEntry[];
  skills?: SkillCategory[];
  experience?: ExperienceEntry[];
  projects?: ProjectEntry[];
  languages?: { [language: string]: string };
  extra_curricular?: string[];
}

export interface SkillCategory {
  category: string;    // Programming Languages", "Backend Frameworks"
  skills: string[];    // list of skills in that category
}

export interface EducationEntry {
  degree: string;
  school?: string;
  institution?: string;
  year: string;
  coursework?: string;
}

export interface ExperienceEntry {
  title: string;
  company?: string;
  period?: string;
  location?: string;
  tags?: string[];
  bullets?: string[];
}

export interface ProjectEntry {
  name: string;
  description?:string;
  url?: string;
  year?: string;
  tags?: string[];
  bullets?: string[];
}
