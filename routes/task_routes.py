from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models import Task, TaskCreate, TaskUpdate
from storage import task_storage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=201)
def create_task(task_data: TaskCreate):
    """Create a new task"""
    try:
        task = task_storage.create_task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority
        )
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=List[Task])
def list_tasks(
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    status: Optional[str] = Query(None, regex="^(pending|in_progress|completed)$")
):
    """List all tasks with optional filtering by priority and status"""
    try:
        tasks = task_storage.get_all_tasks(priority=priority, status=status)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str):
    """Get a specific task by ID"""
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return task


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: str, task_update: TaskUpdate):
    """Update task status"""
    task = task_storage.update_task(task_id, task_update.status)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str):
    """Delete a task"""
    success = task_storage.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return None
