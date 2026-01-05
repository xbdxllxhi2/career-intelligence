from .models import CreateUserApplicationCommand, GetUserApplicationResponse
from jobs.Job import JobDetail
from .entities import UserApplicationEntity

def map_to_entity(input : CreateUserApplicationCommand, job_offer:JobDetail) -> UserApplicationEntity:
    return UserApplicationEntity(
        user_id=1,
        job_offer_id=job_offer.reference,
        company=job_offer.company,
        job_offer_title=job_offer.title,
        job_offer_url=job_offer.job_url,
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
        company=entity.company,
        company_reference=entity.company,
        date=entity.applied_at,
        status=entity.status,
        portal=entity.applied_through,
        rating=entity.application_experience,
        notes=entity.notes
    )
