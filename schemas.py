from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# ===== Регистрация и логин   =======
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str

# ====== Создание самого роадмапа  =======
class RoadmapCreateRequest(BaseModel):
    topic_id: int
    user_id: int

# ====== шаги в роадмапе ========
class StepCreateRequest(BaseModel):
    roadmap_id: int
    parent_step_id: Optional[int] = None
    step_title: str
    step_description: Optional[str] = None
    step_order: int = 0

# ====== информация про шаги в роадмапе ========
class StepResponse(BaseModel):
    step_id: int
    roadmap_id: int
    parent_step_id: Optional[int] = None
    step_title: str
    step_description: Optional[str] = None
    step_order: int
    created_at: datetime

    class Config:
        from_attributes = True

# ===== Комментарии ======

class CommentCreate(BaseModel):
    topic_id: int
    content: str
    parent_comment_id: Optional[int] = None

class CommentResponse(BaseModel):
    comment_id: int
    user_id: int
    topic_id: int
    parent_comment_id: Optional[int]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

