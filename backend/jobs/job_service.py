from typing import List
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pydantic import HttpUrl

from .Job import JobBasic, JobDetail
from models.page import Page
from .filters import JobFilters
from database.engine import engine
DATABASE_URL = "postgresql://ai_readonly:strong_password@localhost:5433/jobsdb"

engine: Engine = engine


def getJobByReference(reference: str) -> JobDetail | None:
    sql = text(
        """
        SELECT
            j.job_checksum AS reference,
            j.title,
            J.job_url,
            j.description,
            j.seniority,
            j.source_apply_url,
            o.name        AS company,
            o.description AS company_description,
            o.org_type    AS company_type,
            o.website     AS company_website,
            o.founded_date AS company_founded_date,
            o.employees  AS company_employees_count,
            o.followers  AS company_followers_count,
            s.name AS source,
            s.domain AS source_domain,
            j.has_easy_apply AS has_direct_apply,
            l.city,
            l.region,
            l.country,
            o.logo_url,
            j.posted_at as created_at,
            j.expires_at
        FROM public.jobs j
        LEFT JOIN public.organizations o
            ON j.organization_id = o.organization_id
        LEFT JOIN public.locations l
            ON j.location_id = l.location_id
        LEFT JOIN public.sources s
            ON j.source_id = s.source_id
        WHERE j.job_checksum = :reference
        LIMIT 1;
        """
    )

    with engine.connect() as conn:
        result = conn.execute(sql, {"reference": reference})
        row = result.fetchone()

    if row:
        return JobDetail.model_validate(dict(row._mapping))
    return None


def getJobs(filters: JobFilters, page: int, size: int) -> Page[JobBasic]:
    limit = size
    offset = page * size

    where_clauses: list[str] = []
    params: dict = {
        "limit": limit,
        "offset": offset,
        "user_id":1,
    }

    # Filters
    if filters.title_contains:
        where_clauses.append("LOWER(j.title) LIKE LOWER(:title)")
        params["title"] = f"%{filters.title_contains}%"
        
    if filters.description_contains:
        where_clauses.append("LOWER(j.description) LIKE LOWER(:description)")
        params["description"] = f"%{filters.description_contains}%"

    if not filters.include_expired:
        where_clauses.append("j.expires_at >= NOW()")

    if filters.has_easy_apply is not None:
        where_clauses.append("j.has_easy_apply = :has_easy_apply")
        params["has_easy_apply"] = filters.has_easy_apply

    if filters.country:
        where_clauses.append("l.country = :country")
        params["country"] = filters.country

    if filters.region:
        where_clauses.append("l.region = :region")
        params["region"] = filters.region

    if filters.city:
        where_clauses.append("l.city = :city")
        params["city"] = filters.city

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    # Main query
    sql = text(
        f"""
        SELECT
            j.job_checksum AS reference,
            j.title,
            j.job_url,
            j.seniority,
            j.source_apply_url,
            o.name AS company,
            o.description AS company_description,
            o.org_type AS company_type,
            o.website AS company_website,
            o.founded_date AS company_founded_date,
            s.name AS source,
            s.domain AS source_domain,
            j.has_easy_apply AS has_direct_apply,
            l.city,
            l.region,
            l.country,
            o.logo_url,
            j.posted_at AS created_at,
            j.expires_at,
            CASE WHEN ua.job_offer_id IS NOT NULL THEN TRUE ELSE FALSE END AS applied
        FROM public.jobs j
        LEFT JOIN public.organizations o ON j.organization_id = o.organization_id
        LEFT JOIN public.locations l ON j.location_id = l.location_id
        LEFT JOIN public.sources s ON j.source_id = s.source_id
        LEFT JOIN app.user_applications ua
            ON ua.job_offer_id = j.job_checksum
            AND ua.user_id = :user_id
        {where_sql}
        ORDER BY j.expires_at ASC
        LIMIT :limit OFFSET :offset
    """
    )

    # Count query (same filters!)
    count_sql = text(
        f"""
        SELECT COUNT(*)
        FROM public.jobs j
        LEFT JOIN public.locations l ON j.location_id = l.location_id
        {where_sql}
    """
    )

    with engine.connect() as conn:
        rows = conn.execute(sql, params).mappings().all()
        total = conn.execute(count_sql, params).scalar_one()

    items = [JobBasic.model_validate(row) for row in rows]

    return Page[JobBasic](
        content=items,
        page=page,
        size=size,
        totalElements=total,
        totalPages=(total + size - 1) // size,
    )
