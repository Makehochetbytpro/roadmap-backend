import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str

class RoadmapCreateRequest(BaseModel):
    topic_id: int
    user_id: int

class StepCreateRequest(BaseModel):
    roadmap_id: int
    parent_step_id: Optional[int] = None
    step_title: str
    step_description: Optional[str] = None
    step_order: int = 0

class StepResponse(BaseModel):
    step_id: int
    roadmap_id: int
    parent_step_id: Optional[int] = None
    step_title: str
    step_description: Optional[str] = None
    step_order: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

