export interface JobFilters {
  title_contains?: string;
  description_contains?:string;
  include_expired?: boolean;
  has_easy_apply?: boolean;
  country?: string;
  region?: string;
  city?: string;
}
