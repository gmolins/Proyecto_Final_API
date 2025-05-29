from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select

from db.database import get_session
from models.todo import TodoList, TodoCreate, TodoRead
from models.user import User
from crud.user import get_user_by_name
from crud.todo import (
    create_todolist,
    get_todos,
    get_todolist_by_id,
    update_todolist,
    delete_todolist,
    get_todolist_by_title,
    update_todolist_by_title,
    delete_todolist_by_title,
    get_todos_by_user_name,
)
from auth.dependencies import get_current_user, require_role  # Import role-based dependency

router = APIRouter()

@router.post("/", response_model=TodoRead)
def create(todo: TodoCreate, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    try:
        # Use the function from CRUD to get the user by name
        user = get_user_by_name(session, todo.user_name)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with name '{todo.user_name}' not found")
        
        # Create the entry with the user's ID
        todo_data = TodoList(**todo.model_dump(exclude={"user_name"}), user_id=user.id, created_at=datetime.now())
        created_todo = create_todolist(session, todo_data)
        session.refresh(created_todo)  # Refresh to load relationships
        return created_todo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/", response_model=list[TodoRead])
def read_all(session: Session = Depends(get_session)):
    try:
        return get_todos(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{todolist_id}", response_model=TodoRead)
def read(todolist_id: int, session: Session = Depends(get_session)):
    try:
        todolist = get_todolist_by_id(session, todolist_id)
        if not todolist:
            raise HTTPException(status_code=404, detail=f"Todo-list with ID {todolist_id} not found")
        return todolist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/title/{title}", response_model=TodoRead)
def read_by_title(title: str, session: Session = Depends(get_session)):
    try:
        todolist = get_todolist_by_title(session, title)
        if not todolist:
            raise HTTPException(status_code=404, detail=f"Todo-list with title '{title}' not found")
        return todolist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/user/{user_name}", response_model=list[TodoRead])
def read_by_user_name(user_name: str, session: Session = Depends(get_session)):
    try:
        todos = get_todos_by_user_name(session, user_name)
        if not todos:
            raise HTTPException(status_code=404, detail=f"No Todo-Lists found for user '{user_name}'")
        return todos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/{todo_id}", response_model=TodoList)
def update(
    todo_id: int,
    todo_data: dict = Body(
        ...,
        examples=[
            {
                "title": "Updated Todo-List Title",
                "content": "Updated content for the Todo-List"
            }
        ]
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        updated_todo = update_todolist(session, todo_id, todo_data)
        if not updated_todo:
            raise HTTPException(status_code=404, detail=f"Todo-List with ID {todo_id} not found")
        return updated_todo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/title/{title}", response_model=TodoList)
def update_by_title(
    title: str,
    todo_data: dict = Body(
        ...,
        examples=[
            {
                "title": "Updated Todo-List Title",
                "content": "Updated content for the Todo-List"
            }
        ]
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        updated_todo = update_todolist_by_title(session, title, todo_data)
        if not updated_todo:
            raise HTTPException(status_code=404, detail=f"Todo-List with title '{title}' not found")
        return updated_todo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/{todolist_id}", response_model=TodoList)
def delete(todolist_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    try:
        deleted_todolist = delete_todolist(session, todolist_id)
        if not deleted_todolist:
            raise HTTPException(status_code=404, detail=f"Todo-List with ID {todolist_id} not found")
        return deleted_todolist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/title/{title}", response_model=TodoList)
def delete_by_title(title: str, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    try:
        deleted_todolist = delete_todolist_by_title(session, title)
        if not deleted_todolist:
            raise HTTPException(status_code=404, detail=f"Todo-List with title '{title}' not found")
        return deleted_todolist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")