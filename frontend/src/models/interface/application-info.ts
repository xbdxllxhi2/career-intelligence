export enum ApplicationStatus {
  APPLIED = 'APPLIED',
  REJECTED = 'REJECTED',
  ACCEPTED = 'ACCEPTED',
  INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED',
}

export interface UserApplicationInfo {
  id?: string;
  job_reference?: string;
  job_title?:string,
  job_country?:string,
  job_region?:string,
  job_city?:string,
  company?:string,
  company_logo_url?:string,
  job_offer_url?:string,
  applied_at?: Date;
  applied_through?: string;
  application_experience?: number;
  notes?: string;
  status: string;
}


export interface saveApplicationRequest{
  job_reference: string;
  date: Date;
  portal: string;
  rating: number;
  notes: string;
}
