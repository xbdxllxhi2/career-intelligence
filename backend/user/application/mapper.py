from .models import CreateUserApplicationCommand, GetUserApplicationResponse
from jobs.Job import JobDetail
from .entities import UserApplicationEntity

def map_to_entity(input : CreateUserApplicationCommand, job_offer:JobDetail) -> UserApplicationEntity:
    return UserApplicationEntity(
        user_id=1,
        job_offer_id=job_offer.reference,
        company=job_offer.company,
        company_logo_url=job_offer.logo_url,
        job_offer_title=job_offer.title,
        job_offer_url=job_offer.job_url,
        job_offer_country=job_offer.country,
        job_offer_region=job_offer.region,
        job_offer_city=job_offer.city,
        applied_at=input.date,
        applied_through=input.portal,
        application_experience=input.rating,
        notes=input.notes
    )


def map_to_model(entity: UserApplicationEntity) -> GetUserApplicationResponse:
    return GetUserApplicationResponse(
        id=entity.id,
        job_reference=entity.job_offer_id,
        job_title=entity.job_offer_title,
        job_country=entity.job_offer_country,
        job_region=entity.job_offer_region,
        job_city=entity.job_offer_city,
        company=entity.company,
        company_logo_url=entity.company_logo_url,
        date=entity.applied_at,
        status=entity.status,
        portal=entity.applied_through,
        notes=entity.notes
    )
