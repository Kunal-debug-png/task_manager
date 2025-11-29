from typing import Dict, List, Optional
from models import Task, SubTask
from datetime import datetime
from uuid import uuid4


class TaskStorage:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.subtasks: Dict[str, List[SubTask]] = {}
    
    def create_task(self, title: str, description: str, priority: str) -> Task:
        task_id = str(uuid4())
        now = datetime.now()
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            status="pending",
            created_at=now,
            updated_at=now
        )
        self.tasks[task_id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self, priority: Optional[str] = None, status: Optional[str] = None) -> List[Task]:
        tasks = list(self.tasks.values())
        
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return tasks
    
    def update_task(self, task_id: str, status: str) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.now()
        return task
    
    def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            if task_id in self.subtasks:
                del self.subtasks[task_id]
            return True
        return False
    
    def create_subtasks(self, parent_task_id: str, subtask_titles: List[str]) -> List[SubTask]:
        if parent_task_id not in self.tasks:
            return []
        
        if len(subtask_titles) != 3:
            raise ValueError("Exactly 3 subtasks are required")
        
        subtasks = []
        now = datetime.now()
        
        for title in subtask_titles:
            subtask_id = str(uuid4())
            subtask = SubTask(
                id=subtask_id,
                parent_task_id=parent_task_id,
                title=title,
                status="pending",
                created_at=now,
                updated_at=now
            )
            subtasks.append(subtask)
        
        self.subtasks[parent_task_id] = subtasks
        return subtasks
    
    def get_subtasks(self, parent_task_id: str) -> List[SubTask]:
        return self.subtasks.get(parent_task_id, [])
    
    def get_subtask(self, parent_task_id: str, subtask_id: str) -> Optional[SubTask]:
        subtasks = self.subtasks.get(parent_task_id, [])
        for subtask in subtasks:
            if subtask.id == subtask_id:
                return subtask
        return None
    
    def update_subtask(self, parent_task_id: str, subtask_id: str, status: str) -> Optional[SubTask]:
        subtasks = self.subtasks.get(parent_task_id, [])
        for subtask in subtasks:
            if subtask.id == subtask_id:
                subtask.status = status
                subtask.updated_at = datetime.now()
                return subtask
        return None

task_storage = TaskStorage()
