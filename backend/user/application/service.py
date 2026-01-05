from . import repository
from . import mapper
from .models import CreateUserApplicationCommand
from jobs import job_service


def save_user_application(command: CreateUserApplicationCommand) -> None:
    job_offer = job_service.getJobByReference(command.job_reference)
    entity = mapper.map_to_entity(command, job_offer)
    repository.save_user_application(entity)


def get_user_application_by_id():
    pass


def get_user_applications() -> list:
    return [
        mapper.map_to_model(record) for record in repository.get_user_applications()
    ]


def delete_user_application(application_id: int) -> None:
    repository.delete_user_application(application_id)
