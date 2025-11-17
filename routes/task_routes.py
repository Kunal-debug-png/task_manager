from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models import Task, TaskCreate, TaskUpdate
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
2. 3-5 potential sub-tasks
3. Categorize into one of: Bug Fix, Feature, DevOps, Documentation, Research, Testing

Task Details:
- Title: {task.title}
- Description: {task.description}
- Priority: {task.priority}

Format your response as JSON:
{{
  "summary": "one sentence summary",
  "sub_tasks": ["subtask 1", "subtask 2", "subtask 3"],
  "category": "category name"
}}
"""
                
                print(f"\nCalling Gemini 2.5 Flash API...")
                
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                gemini_output = response.text.strip()
                
                
                if "```json" in gemini_output:
                    gemini_output = gemini_output.split("```json")[1].split("```")[0].strip()
                elif "```" in gemini_output:
                    gemini_output = gemini_output.split("```")[1].split("```")[0].strip()
                
                result = json.loads(gemini_output)
                
                
                print(f" GEMINI 2.5 FLASH OUTPUT")
                print(f"Summary: {result.get('summary')}")
                print(f"Category: {result.get('category')}")
                print(f"\nSub-tasks:")
                for i, subtask in enumerate(result.get('sub_tasks', []), 1):
                    print(f"   {i}. {subtask}")
                
                
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
