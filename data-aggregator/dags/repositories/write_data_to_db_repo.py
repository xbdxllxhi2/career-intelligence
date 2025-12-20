from airflow.providers.postgres.hooks.postgres import PostgresHook
from mappers.map_rllinkedin_jobs import map_linkedin_job
from repositories.read_jobs_from_file import get_jobs_dict
import json

def export_to_postgres(jobs_file_path="/opt/airflow/output/jobs/jobs.json"):
    jobs = (map_linkedin_job(j) for j in get_jobs_dict(file=jobs_file_path).values())

    for j in jobs:
        org_data, source_data, location_data, job_data = j.organization, j.source, j.location, j.job

        hook = PostgresHook(postgres_conn_id="my_postgres")

        # 1. Insert or get org_id
        org_id = hook.get_first(
            "SELECT organization_id FROM organizations WHERE name=%s", 
            parameters=(org_data.name,)
        )
        if not org_id:
            org_id = hook.get_first(
                """
                INSERT INTO organizations (name, website, logo_url, industry, size_bucket, employees)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING organization_id
                """,
                parameters=(
                    org_data.name,
                    str(org_data.website),
                    str(org_data.logo),
                    org_data.industry,
                    org_data.size_bucket,
                    org_data.employees
                )
            )

        # 2. Insert or get source_id
        source_id = hook.get_first(
            "SELECT source_id FROM sources WHERE name=%s AND domain=%s",
            parameters=(source_data.name, source_data.source_domain)
        )
        if not source_id:
            source_id = hook.get_first(
                "INSERT INTO sources (name, domain, source_type) VALUES (%s,%s,%s) RETURNING source_id",
                parameters=(source_data.name, source_data.source_domain, source_data.source_type)
            )
           

        # 3. Insert or get location_id
        location_id = hook.get_first(
            "SELECT location_id FROM locations WHERE country=%s AND region=%s AND city=%s AND lat=%s AND lng=%s",
            parameters=(location_data.country, location_data.region, location_data.city, location_data.lat, location_data.lng)
        )
        if not location_id:
            location_id = hook.get_first(
                """
                INSERT INTO locations (country, region, city, lat, lng, timezone)
                VALUES (%s, %s, %s, %s, %s, %s)  RETURNING location_id
                """,
                parameters=(
                    location_data.country, location_data.region, location_data.city,
                    location_data.lat, location_data.lng, location_data.timezone
                )
            )

        # 4. Insert job (skip if checksum exists)
        existing_job = hook.get_first(
            "SELECT job_id FROM jobs WHERE job_checksum=%s",
            parameters=(job_data.job_checksum,)
        )
        if not existing_job:
            hook.run(
                """
                INSERT INTO jobs
                (title, description, job_url, external_id, seniority, employment_type, remote, posted_at, expires_at, source_id, organization_id, location_id, has_easy_apply, job_checksum, raw)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                parameters=(
                    job_data.title, job_data.description, str(job_data.url), j.source.external_id,
                    job_data.seniority, job_data.employment_type, job_data.is_remote,
                    job_data.posted_at, job_data.expires_at,
                    source_id, org_id, location_id, job_data.has_easy_apply, job_data.job_checksum, json.dumps(j.raw)
                )
            )
