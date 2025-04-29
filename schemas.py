from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from pydantic import root_validator
import json

# ===== Регистрация и логин   =======
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str

#========= Получение всех категории ========
class CategoryOut(BaseModel):
    category_id: int
    name: str

    class Config:
        from_attributes = True

# ======== ПОЛУЧЕНИЕ ВСЕХ ТОПИКОВ =========
class TopicRead(BaseModel):
    topic_id: int
    name: str
    description: Optional[str] = None
    like_count: int
    dislike_count: int
    category_id: int
    image: Optional[bytes] = None  

    class Config:
        from_attributes = True

# =========== Получение всех категории вместе с топиком =========

class CategoryWithTopics(BaseModel):
    category_id: int
    name: str
    topics: List[TopicRead]  # Список топиков, которые принадлежат категории

    class Config:
        from_attributes = True

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

# ======= Материалы в каждом Шаге =========

class StepMaterialBase(BaseModel):
    roadmap_id: int
    step_id: int
    name: str
    description: Optional[str] = None
    tip: Optional[str] = None
    videos: Optional[List[str]] = Field(default_factory=list)
    books: Optional[List[str]] = Field(default_factory=list)
    completed: bool = False


class StepMaterialCreate(StepMaterialBase):
    pass


class StepMaterialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tip: Optional[str] = None
    videos: Optional[List[str]] = None
    books: Optional[List[str]] = None
    completed: Optional[bool] = None



class StepMaterialOut(StepMaterialBase):
    material_id: int
    created_at: datetime

    @root_validator(pre=True)
    def convert_string_fields_to_lists(cls, values):
        for field in ['videos', 'books']:
            val = getattr(values, field, None)
            if isinstance(val, str):
                try:
                    setattr(values, field, json.loads(val))
                except json.JSONDecodeError:
                    setattr(values, field, [])
        return values

    class Config:
        from_attributes = True

# ====== CommunityRoadmap =========

class CommunityRoadmapBase(BaseModel):
    topic_id: int
    proposed_steps: str

class CommunityRoadmapCreate(CommunityRoadmapBase):
    pass

class CommunityRoadmapUpdate(CommunityRoadmapBase):
    upvotes: Optional[int] = None
    downvotes: Optional[int] = None

class CommunityRoadmapInDB(CommunityRoadmapBase):
    c_roadmap_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ======== Vote for CommunityRoadmap ==============
class VoteBase(BaseModel):
    user_id: int
    c_roadmap_id: int
    vote_type: str  # "upvote" or "downvote"

class VoteCreate(VoteBase):
    pass

class VoteInDB(VoteBase):
    vote_id: int

    class Config:
        from_attributes = True
