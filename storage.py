from typing import Dict, List, Optional
from models import Task
from datetime import datetime
from uuid import uuid4


class TaskStorage:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
    
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
            return True
        return False

task_storage = TaskStorage()
