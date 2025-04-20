import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pydantic import BaseModel
from typing import List
from database import SessionLocal
from models import Topic, Roadmap, User,Step
from schemas import RoadmapCreateRequest, StepCreateRequest, StepResponse
from auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================== ЭНДПОИНТЫ ==========================

# Проверить таблицы в базе
@app.get("/check_tables")
def check_tables(db: Session = Depends(get_db)):
    tables = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).fetchall()
    return {"tables": [table[0] for table in tables]}

# Модель запроса для создания категории
class CategoryCreate(BaseModel):
    name: str

# Создать новую категорию
@app.post("/create_category")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db.execute(text('INSERT INTO "Category" (name) VALUES (:name)'), {"name": category.name})
    db.commit()
    return {"message": "Category created successfully", "category": category.name}

# ====================== БАЙЕСОВСКИЙ АЛГОРИТМ ======================

class RoadmapScoreModel(BaseModel):
    name: str
    likes: int
    dislikes: int

    def dict_with_score(self, C: float = 0.5, m: int = 50):
        bayesian_score = (self.likes + C * m) / (self.likes + self.dislikes + m)
        return {**self.dict(), "bayesian_score": bayesian_score}

# Модель запроса для списка роадмапов
class RoadmapListRequest(BaseModel):
    roadmaps: List[RoadmapScoreModel]

# Эндпоинт для ранжирования роадмапов
@app.post("/rank")
def rank_roadmaps(data: RoadmapListRequest):
    roadmaps_with_scores = [roadmap.dict_with_score() for roadmap in data.roadmaps]
    sorted_roadmaps = sorted(roadmaps_with_scores, key=lambda x: x["bayesian_score"], reverse=True)
    return {"bayesian_ranking": sorted_roadmaps}

# Лайкнуть топик
@app.post("/topics/{topic_id}/like")
def like_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic.like_count += 1
    db.commit()
    return {"message": "Liked!", "like_count": topic.like_count}

# Дизлайкнуть топик
@app.post("/topics/{topic_id}/dislike")
def dislike_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic.dislike_count += 1
    db.commit()
    return {"message": "Disliked!", "dislike_count": topic.dislike_count}

# Создать роадмап
@app.post("/create_roadmap")
def create_roadmap(request: RoadmapCreateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    topic = db.query(Topic).filter(Topic.topic_id == request.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    new_roadmap = Roadmap(
        topic_id=request.topic_id,
        user_id=request.user_id,
        created_at=datetime.datetime.utcnow()
    )

    db.add(new_roadmap)
    db.commit()
    db.refresh(new_roadmap)

    return {"message": "Roadmap created successfully", "roadmap": {
        "roadmap_id": new_roadmap.roadmap_id,
        "topic_id": new_roadmap.topic_id,
        "user_id": new_roadmap.user_id,
        "created_at": new_roadmap.created_at
    }}


# Создание шага
@app.post("/create_step", response_model=StepResponse)
def create_step(step: StepCreateRequest, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(Roadmap.roadmap_id == step.roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    if step.parent_step_id:
        parent_step = db.query(Step).filter(Step.step_id == step.parent_step_id).first()
        if not parent_step:
            raise HTTPException(status_code=404, detail="Parent Step not found")

    new_step = Step(
        roadmap_id=step.roadmap_id,
        parent_step_id=step.parent_step_id,
        step_title=step.step_title,
        step_description=step.step_description,
        step_order=step.step_order,
        created_at=datetime.datetime.utcnow()
    )

    db.add(new_step)
    db.commit()
    db.refresh(new_step)

    return new_step

# Получить все шаги роадмапа
@app.get("/roadmap/{roadmap_id}", response_model=list[StepResponse])
def get_steps_by_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    steps = db.query(Step).filter(Step.roadmap_id == roadmap_id).order_by(Step.step_order).all()
    return steps
