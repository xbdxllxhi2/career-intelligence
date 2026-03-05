from database.engine import SessionLocal
from .entities import UserApplicationEntity


def save_user_application(application: UserApplicationEntity) -> None:
    with SessionLocal() as session:
        session.add(application)
        session.commit()
        
        
def get_user_applications(user_id: str) -> list[UserApplicationEntity]:
    with SessionLocal() as session:
        return session.query(UserApplicationEntity).filter_by(user_id=user_id).all()
    
    
def delete_user_application(user_id: str, application_id: int) -> None:
    with SessionLocal() as session:
        application = session.query(UserApplicationEntity).filter_by(
            id=application_id, user_id=user_id
        ).first()
        if application:
            session.delete(application)
            session.commit()