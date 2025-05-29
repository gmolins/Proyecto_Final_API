from sqlmodel import Session, select
from models.todo import TodoList
from models.user import User
from crud.user import get_user_by_name

def create_todolist(session: Session, todolist: TodoList):
    existing_todolist = session.exec(select(TodoList).where(TodoList.title == todolist.title)).first()
    if existing_todolist:
        raise ValueError(f"A todo-list with title '{todolist.title}' already exists.")
    session.add(todolist)
    session.commit()
    session.refresh(todolist)
    return todolist

def get_todos(session: Session):
    return session.exec(select(TodoList)).all()

def get_todolist_by_id(session: Session, todolist_id: int):
    return session.get(TodoList, todolist_id)

def get_todolist_by_title(session: Session, title: str):
    statement = select(TodoList).where(TodoList.title == title)
    return session.exec(statement).first()

def update_todolist(session: Session, todolist_id: int, todolist_data: dict):
    todolist = session.get(TodoList, todolist_id)
    if not todolist:
        return None
    for key, value in todolist_data.items():
        setattr(todolist, key, value)
    session.commit()
    session.refresh(todolist)
    return todolist

def update_todolist_by_title(session: Session, title: str, todolist_data: dict):
    statement = select(TodoList).where(TodoList.title == title)
    todolist = session.exec(statement).first()
    if not todolist:
        return None
    for key, value in todolist_data.items():
        setattr(todolist, key, value)
    session.commit()
    session.refresh(todolist)
    return todolist

def delete_todolist(session: Session, todolist_id: int):
    todolist = session.get(TodoList, todolist_id)
    if todolist:
        session.delete(todolist)
        session.commit()
    return todolist

def delete_todolist_by_title(session: Session, title: str):
    statement = select(TodoList).where(TodoList.title == title)
    todolist = session.exec(statement).first()
    if todolist:
        session.delete(todolist)
        session.commit()
    return todolist

def get_todos_by_user_name(session: Session, user_name: str):
    user = get_user_by_name(session, user_name)
    if not user:
        return []
    statement = select(TodoList).where(TodoList.user_id == user.id)
    return session.exec(statement).all()