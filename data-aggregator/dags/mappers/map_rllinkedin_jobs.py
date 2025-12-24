from datetime import datetime
from typing import Any, Dict, Optional
from models.local_schemaV1 import Job, Job, JobSchema, Location, Organization, Source


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", ""))
    except Exception:
        return None


def map_linkedin_job(raw: Dict[str, Any]) -> JobSchema:
    return JobSchema(
        job_id=raw.get("id"),
        source=map_source(raw),
        job=_map_job_details(raw),
        organization=_map_organization(raw),
        location=_map_location(raw),
        raw=raw,  # full payload preserved
    )


def map_source(raw: Dict[str, Any]) -> Source:
    return Source(
        name=raw.get("source",""),
        source_domain=raw.get("source_domain",""),
        source_type=raw.get("source_type",""),
        external_id=str(raw.get("id")),
        url=raw.get("url"),
        fetched_at=parse_datetime(raw.get("fetched_at")),
    )


def _map_job_details(raw: Dict[str, Any]) -> Job:
    return Job(
        title=raw.get("title"),
        job_checksum=raw.get("checksum"),
        description=raw.get("description_text", ""),
        url=raw.get("external_apply_url", ""),
        seniority=raw.get("seniority"),
        employment_type=raw.get("employment_type", []),
        location_type=raw.get("location_type"),
        domain=raw.get("domain"),
        posted_at=parse_datetime(raw.get("posted_at")),
        expires_at=parse_datetime(raw.get("date_validthrough")),
        remote_type=raw.get("remote_type"),
        is_remote=raw.get("is_remote"),
        has_easy_apply= raw.get("directapply")
    )

def _map_organization(raw: Dict[str, Any]) -> Optional[Organization]:
    org_name = raw.get("organization")
    if not org_name:
        return None

    return Organization(
        name=org_name,
        logo=raw.get("organization_logo"),
        industry=raw.get("linkedin_org_industry"),
        slogan=raw.get("linkedin_org_slogan"),
        size_bucket=raw.get("linkedin_org_size"),
        website=raw.get("linkedin_org_url"),
        description=raw.get("linkedin_org_description"),
        type=raw.get("linkedin_org_type"),
        employees=raw.get("linkedin_org_employees"),
        followers=raw.get("linkedin_org_followers"),
        founded_date=parse_datetime(raw.get("linkedin_org_foundeddate")),
        specialities=raw.get("linkedin_org_specialties", []),
    )


def _map_location(raw: Dict[str, Any]) -> Optional[Location]:
    # Prefer derived fields (cleaner)
    if raw.get("cities_derived"):
        return Location(
            country=raw.get("countries_derived", [None])[0],
            region=raw.get("regions_derived", [None])[0],
            city=raw.get("cities_derived", [None])[0],
            lat=raw.get("lats_derived", [None])[0],
            lng=raw.get("lngs_derived", [None])[0],
            timezone=raw.get("timezones_derived", [None])[0],
        )

    # Fallback to raw structured location
    locations = raw.get("locations_raw")
    if locations:
        loc = locations[0]
        addr = loc.get("address", {})
        return {
            "country": addr.get("addressCountry"),
            "region": addr.get("addressRegion"),
            "city": addr.get("addressLocality"),
            "lat": loc.get("latitude"),
            "lng": loc.get("longitude"),
        }

    return None
