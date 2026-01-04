export enum ApplicationStatus {
  APPLIED = 'APPLIED',
  REJECTED = 'REJECTED',
  ACCEPTED = 'ACCEPTED',
  INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED',
}

export interface UserApplicationInfo {
  reference?: string;
  jobReference?: string;
  date?: Date;
  portal?: string;
  rating?: number;
  uploadedResumeReference?: string;
  notes?: string;
  status: ApplicationStatus;
}


export interface saveApplicationRequest{
  job_reference: string;
  date: Date;
  portal: string;
  rating: number;
  notes: string;
}
