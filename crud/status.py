from sqlmodel import Session, select
from models.status import Status

def create_status(session: Session, status: Status):
    existing_status = session.exec(select(Status).where(Status.name == status.name)).first()
    if existing_status:
        raise ValueError(f"A status with name '{status.name}' already exists.")
    session.add(status)
    session.commit()
    session.refresh(status)
    return status

def get_status(session: Session):
    return session.exec(select(Status)).all()

def get_status_by_id(session: Session, status_id: int):
    return session.get(Status, status_id)

def get_status_by_name(session: Session, name: str):
    statement = select(Status).where(Status.name == name)
    return session.exec(statement).first()

def update_status_by_id(session: Session, status_id: int, status_data: dict):
    status = session.get(Status, status_id)
    if not status:
        return None
    for key, value in status_data.items():
        setattr(status, key, value)
    session.commit()
    session.refresh(status)
    return status

def delete_status_by_id(session: Session, id: int):
    statement = select(Status).where(Status.id == id)
    status = session.exec(statement).first()
    if status:
        session.delete(status)
        session.commit()
    return status