from . import repository
from . import mapper
from .models import CreateUserApplicationCommand
from jobs import job_service


def save_user_application(user_id: str, command: CreateUserApplicationCommand) -> None:
    job_offer = job_service.getJobByReference(command.job_reference)
    entity = mapper.map_to_entity(user_id, command, job_offer)
    repository.save_user_application(entity)


def get_user_application_by_id():
    pass


def get_user_applications(user_id: str) -> list:
    return [
        mapper.map_to_model(record) for record in repository.get_user_applications(user_id)
    ]


def delete_user_application(user_id: str, application_id: int) -> None:
    repository.delete_user_application(user_id, application_id)
