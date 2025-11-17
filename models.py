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
    sub_tasks: list[str]
    category: str


class Task(BaseModel):
    id: str
    title: str
    description: str
    priority: Literal["low", "medium", "high"]
    status: Literal["pending", "in_progress", "completed"] = "pending"
    created_at: datetime
    updated_at: datetime
