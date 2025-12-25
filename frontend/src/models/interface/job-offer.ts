export interface JobOffer {
    reference: string;
    title: string;
    company?: string;
    org_description?: string;
    country?: string;
    region?: string;
    city?: string;
    description?: string;
    logo_url?: string;
    job_url?:string
    created_at?:Date
}

