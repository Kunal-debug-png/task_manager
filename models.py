from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    priority: Literal["low", "medium", "high"]


class TaskUpdate(BaseModel):
    status: Literal["pending", "in_progress", "completed"]


class GeminiResponse(BaseModel):
    summary: str
    sub_tasks: list[str] = Field(..., min_length=3, max_length=3)
    category: str


class SubTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class SubTaskUpdate(BaseModel):
    status: Literal["pending", "in_progress", "completed"]


class SubTask(BaseModel):
    id: str
    parent_task_id: str
    title: str
    status: Literal["pending", "in_progress", "completed"] = "pending"
    created_at: datetime
    updated_at: datetime


class Task(BaseModel):
    id: str
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
    status: Literal["pending", "in_progress", "completed"] = "pending"
    created_at: datetime
    updated_at: datetime

class TaskResultGemini(BaseModel):
    summary: str = Field(..., description="A brief one-sentence summary of the task")
    sub_tasks: list[str] = Field(..., description="Exactly 3 potential sub-tasks")
    category: Literal["Bug Fix", "Feature", "DevOps", "Documentation", "Research", "Testing"] = Field(..., description="Task category")

