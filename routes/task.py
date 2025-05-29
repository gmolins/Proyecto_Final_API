from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select

from db.database import get_session
from models.task import Task, TaskRead, TaskCreate
from crud.todo import get_todolist_by_id
from crud.task import (
    create_task,
    delete_task,
    get_tasks,
    get_task_by_id,
    get_task_by_title,
    get_tasks_from_todo_list,
    update_task,
)
from auth.dependencies import get_current_user, require_role  # Import role-based dependency

router = APIRouter()

@router.post("/", response_model=TaskRead)
def create(task: TaskCreate, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    try:
        todo = get_todolist_by_id(session, task.todolist_id)
        if not todo:
            raise HTTPException(status_code=404, detail=f"Todo-List with ID '{task.todolist_id}' not found")
        
        # Create the task with the Todo-List ID
        task_data = Task(**task.model_dump(), created_at=datetime.now())
        created_task = create_task(session, task_data)
        session.refresh(created_task)  # Refresh to load relationships
        return created_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/", response_model=list[TaskRead])
def read_all(session: Session = Depends(get_session)):
    try:
        return get_tasks(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{task_id}", response_model=TaskRead)
def read(task_id: int, session: Session = Depends(get_session)):
    try:
        task = get_task_by_id(session, task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/title/{title}", response_model=TaskRead)
def read_by_title(title: str, session: Session = Depends(get_session)):
    try:
        todolist = get_task_by_title(session, title)
        if not todolist:
            raise HTTPException(status_code=404, detail=f"Todo-list with title '{title}' not found")
        return todolist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/todo/{todo_list_id}", response_model=list[TaskRead])
def read_by_todo_id(todo_list_id: int, session: Session = Depends(get_session)):
    try:
        tasks = get_tasks_from_todo_list(session, todo_list_id)
        if not tasks:
            raise HTTPException(status_code=404, detail=f"No Todo-Lists found for ID '{todo_list_id}'")
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/{task_id}", response_model=Task)
def update(
    task_id: int,
    task_data: dict = Body(
        ...,
        examples=[
            {
                "title": "Updated Task Title",
                "content": "Updated content for the Task"
            }
        ]
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        updated_task = update_task(session, task_id, task_data)
        if not updated_task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/{task_id}", response_model=Task)
def delete(task_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    try:
        deleted_task = delete_task(session, task_id)
        if not deleted_task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
        return deleted_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")