export interface JobOffer {
    reference: string;
    title: string;
    seniority?: string;
    company?: string;
    company_description?: string;
    company_foundeddate?:Date,
    company_employees_count?:number,
    company_followers_count?:number
    country?: string;
    region?: string;
    city?: string;
    description?: string;
    logo_url?: string;
    job_url?:string
    source_apply_url?:String
    source?:string
    has_direct_apply?:boolean
    created_at?:Date
    expires_at?:Date
    applied?:boolean
}

