enum ApplicationStatus {
  APPLIED = 'APPLIED',
  REJECTED = 'REJECTED',
  ACCEPTED = 'ACCEPTED',
  INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED',
}

export interface ApplicationInfo {
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
  jobReference: string;
  date: Date;
  portal: string;
  rating: number;
  notes: string;
}
