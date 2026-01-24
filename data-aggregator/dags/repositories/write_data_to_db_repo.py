from airflow.providers.postgres.hooks.postgres import PostgresHook
from mappers.map_rllinkedin_jobs import map_linkedin_job
from repositories.read_jobs_from_file import get_jobs_dict
import json
from models.local_schemaV1 import Job, JobSchema, Location, Organization, Source


def  export_to_postgres(jobs_file_path="/opt/airflow/output/jobs/jobs.json"):
    jobs:list[JobSchema]= [map_linkedin_job(j) for j in get_jobs_dict(file=jobs_file_path).values()]
    hook = PostgresHook(postgres_conn_id="my_postgres")
    
    for j in jobs:
        org_data, source_data, location_data, job_data = j.organization, j.source, j.location, j.job

        # 1. Insert or get org_id
        org_id = hook.get_first(
            "SELECT organization_id FROM organizations WHERE name=%s", 
            parameters=(org_data.name,)
        )
        if not org_id:
            org_id = hook.get_first(
                """
                INSERT INTO organizations (name, logo_url, industry, slogan,
                size_bucket, website, description, org_type, employees, followers,
                founded_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING organization_id
                """,
                parameters=(
                    org_data.name,
                    str(org_data.logo),
                    org_data.industry,
                    org_data.slogan,
                    org_data.size_bucket,
                    str(org_data.website),
                    org_data.description,
                    org_data.type,
                    org_data.employees,
                    org_data.followers,
                    org_data.founded_date
                )
            )
            
            # Inserting specialities
            for spec_name in org_data.specialities:
                hook.run(
                    """
                    INSERT INTO specialities (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                    """,
                    parameters=(spec_name,)
                )
                
            speciality_ids = hook.get_pandas_df(
                """
                SELECT speciality_id, name
                FROM specialities
                WHERE name = ANY(%s)
                """,
                parameters=(org_data.specialities,)
            )['speciality_id'].tolist()
            
            for spec_id in speciality_ids:
                hook.run(
                    """
                    INSERT INTO organization_specialities (organization_id, speciality_id)
                    VALUES (%s, %s)
                    ON CONFLICT (organization_id, speciality_id) DO NOTHING
                    """,
                    parameters=(org_id, spec_id)
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
            job_id = hook.get_first(
                """
                INSERT INTO jobs
                (title, description, job_url, source_apply_url, external_id, seniority, remote, posted_at, expires_at, source_id, organization_id, location_id, has_easy_apply, job_checksum, raw)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)  RETURNING job_id
                """,
                parameters=(
                    job_data.title, job_data.description, str(job_data.url), str(job_data.source_apply_url), j.source.external_id,
                    job_data.seniority, job_data.is_remote,
                    job_data.posted_at, job_data.expires_at,
                    source_id, org_id, location_id, job_data.has_easy_apply, job_data.job_checksum, json.dumps(j.raw)
                )
            )
            
            #Inserting emp type
            emp_type_ids = []
            for emp_type in job_data.employment_type or []:
                existing = hook.get_first(
                    "SELECT id FROM employment_types WHERE name=%s",
                    parameters=(emp_type,)
                )
                if existing:
                    emp_type_ids.append(existing)
                else:
                    new_id = hook.get_first(
                        "INSERT INTO employment_types(name) VALUES(%s) RETURNING id",
                        parameters=(emp_type,)
                    )
                    emp_type_ids.append(new_id)

            # 4. Link job to employment types
            for emp_id in emp_type_ids:
                hook.run(
                    """
                    INSERT INTO job_employment_types(job_id, employment_type_id)
                    VALUES(%s,%s)
                    ON CONFLICT DO NOTHING
                    """,
                    parameters=(job_id, emp_id)
                )
