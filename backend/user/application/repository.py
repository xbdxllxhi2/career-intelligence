from database.engine import SessionLocal
from .entities import UserApplicationEntity


def save_user_application(application: UserApplicationEntity) -> None:
    with SessionLocal() as session:
        session.add(application)
        session.commit()
        
        
def get_user_applications() -> list[UserApplicationEntity]:
    with SessionLocal() as session:
        return session.query(UserApplicationEntity).all()
    
    
def delete_user_application(application_id: int) -> None:
    with SessionLocal() as session:
        application = session.get(UserApplicationEntity, application_id)
        if application:
            session.delete(application)
            session.commit()