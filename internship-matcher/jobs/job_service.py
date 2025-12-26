from typing import List
from unittest import result
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pydantic import HttpUrl

from models.Job import JobBasic, JobDetail


DATABASE_URL = "postgresql://ai_readonly:strong_password@localhost:5433/jobsdb"

engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def getJobByReference(reference: str) -> JobDetail | None:
    sql = text(
        """
        SELECT
            j.job_checksum AS reference,
            j.title,
            job_url,
            o.name        AS company,
            j.description,
            l.city,
            l.region,
            l.country,
            o.logo_url,
            j.posted_at as created_at,
            j.expires_at
        FROM jobs j
        LEFT JOIN organizations o
            ON j.organization_id = o.organization_id
        LEFT JOIN locations l
            ON j.location_id = l.location_id
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


def getJobs(limit: int = 50, offset: int = 0) -> List[JobBasic]:
    sql = text(
        """
         SELECT
            j.job_checksum as reference,
            j.title,
            o.name        AS company,
            o.description AS company_description,
            l.city        AS city,
            l.region      AS region,
            l.country     AS country,
            o.logo_url,
            j.posted_at AS created_at,
            j.expires_at
        FROM jobs j
        LEFT JOIN organizations o
            ON j.organization_id = o.organization_id
        LEFT JOIN locations l
            ON j.location_id = l.location_id
        ORDER BY j.posted_at DESC
        LIMIT :limit OFFSET :offset;
        """
    )

    with engine.connect() as conn:
        result = conn.execute(sql, {"limit": limit, "offset": offset})
        rows = [dict(row._mapping) for row in result]

    return [JobBasic.model_validate(row) for row in rows]
