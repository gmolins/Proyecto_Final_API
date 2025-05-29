from sqlmodel import Session, select
from crud.todo import get_todolist_by_id, get_todolist_by_title
from models.task import Task

def create_task(session: Session, task: Task):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_tasks(session: Session):
    return session.exec(select(Task)).all()

def get_task_by_id(session: Session, task_id: int):
    return session.get(Task, task_id)

def get_task_by_title(session: Session, title: str):
    statement = select(Task).where(Task.title == title)
    return session.exec(statement).first()

def get_all_tasks_by_title(session: Session, title: str):
    statement = select(Task).where(Task.title == title)
    return session.exec(statement).all()

def update_task(session: Session, task_id: int, task_data: dict):
    task = session.get(Task, task_id)
    if not task:
        return None
    for key, value in task_data.items():
        setattr(task, key, value)
    session.commit()
    session.refresh(task)
    return task

def delete_task(session: Session, task_id: int):
    task = session.get(Task, task_id)
    if task:
        session.delete(task)
        session.commit()
    return task

def delete_task_by_title(session: Session, title: str):
    statement = select(Task).where(Task.title == title)
    task = session.exec(statement).first()
    if task:
        session.delete(task)
        session.commit()
    return task

def get_tasks_from_todo_list(session: Session, todo_id: int):
    todo = get_todolist_by_id(session, todo_id)
    if not todo:
        return []
    statement = select(Task).where(Task.todolist_id == todo.id)
    return session.exec(statement).all()