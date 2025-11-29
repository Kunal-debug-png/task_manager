from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models import Task, TaskCreate, TaskUpdate, SubTask, SubTaskUpdate,TaskResultGemini
from storage import task_storage
from kafka_publisher import publish_task_event

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=201)
def create_task(task_data: TaskCreate):
    """Create a new task"""
    try:
        from kafka_publisher import flush_producer
        import google.generativeai as genai
        import os
        import json
        
        task = task_storage.create_task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority
        )
        
        print(f" TASK CREATED EVENT")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Description: {task.description}")
        print(f"Priority: {task.priority}")
        print(f"Status: {task.status}")
        
        
       
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY and GEMINI_API_KEY != "your-api-key-here":
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                
                prompt = f"""
Analyze this task and provide:
1. A brief one-sentence summary
2. Exactly 3 potential sub-tasks
3. Categorize into one of: Bug Fix, Feature, DevOps, Documentation, Research, Testing

Task Details:
- Title: {task.title}
- Description: {task.description}
- Priority: {task.priority}
"""
                
                print(f"\nCalling Gemini 2.5 Flash API...")
                
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config={
                        "response_mime_type": "application/json",
                        "response_schema": TaskResultGemini,
                    }
                )
                
                response = model.generate_content(prompt)
                gemini_output = TaskResultGemini.model_validate_json(response.text)
                
                
                print(f" GEMINI 2.5 FLASH OUTPUT")
                print(f"Summary: {gemini_output.summary}")
                print(f"Category: {gemini_output.category}")
                print(f"\nSub-tasks:")
                for i, subtask in enumerate(gemini_output.sub_tasks, 1):
                    print(f"   {i}. {subtask}")
                
                # Ensure exactly 3 subtasks
                subtasks_to_store = gemini_output.sub_tasks[:3]  # Take first 3
                while len(subtasks_to_store) < 3:
                    subtasks_to_store.append(f"Additional subtask {len(subtasks_to_store) + 1}")
                
                task_storage.create_subtasks(task.id, subtasks_to_store)
                print(f"\n✓ 3 subtasks stored for task {task.id}")
                
            except Exception as e:
                print(f"Gemini API error: {e}\n")
        
        
        publish_task_event(
            event_type="task.created",
            task_id=task.id,
            task_data={
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "status": task.status
            }
        )
        
        flush_producer()
        
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


@router.get("/{task_id}/subtasks", response_model=List[SubTask])
def get_subtasks(task_id: str):
    """Get all subtasks for a specific task"""
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    
    subtasks = task_storage.get_subtasks(task_id)
    return subtasks


@router.get("/{task_id}/subtasks/{subtask_id}", response_model=SubTask)
def get_subtask(task_id: str, subtask_id: str):
    """Get a specific subtask"""
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    
    subtask = task_storage.get_subtask(task_id, subtask_id)
    if not subtask:
        raise HTTPException(status_code=404, detail=f"Subtask with id '{subtask_id}' not found")
    
    return subtask


@router.put("/{task_id}/subtasks/{subtask_id}", response_model=SubTask)
def update_subtask(task_id: str, subtask_id: str, subtask_update: SubTaskUpdate):
    """Update a specific subtask status"""
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    
    subtask = task_storage.update_subtask(task_id, subtask_id, subtask_update.status)
    if not subtask:
        raise HTTPException(status_code=404, detail=f"Subtask with id '{subtask_id}' not found")
    
    return subtask
