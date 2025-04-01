from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from sqlalchemy.sql import text
from pydantic import BaseModel
from auth import router as auth_router
import math

app = FastAPI()
app.include_router(auth_router)

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоинт для проверки, какие таблицы есть в базе
@app.get("/check_tables")
def check_tables(db: Session = Depends(get_db)):  
    tables = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).fetchall()
    return {"tables": [table[0] for table in tables]}

# Модель данных для запроса
class CategoryCreate(BaseModel):
    name: str

@app.post("/create_category")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db.execute(text('INSERT INTO "Category" (name) VALUES (:name)'), {"name": category.name})
    db.commit()
    return {"message": "Category created successfully", "category": category.name}

# ====================== БАЙЕСОВСКИЙ АЛГОРИТМ ======================

class Roadmap(BaseModel):
    name: str
    likes: int
    dislikes: int

    def dict_with_score(self, C: float = 0.5, m: int = 50):
        bayesian_score = (self.likes + C * m) / (self.likes + self.dislikes + m)
        return {**self.dict(), "bayesian_score": bayesian_score}

class RoadmapList(BaseModel):
    roadmaps: list[Roadmap]

@app.post("/rank")
def rank_roadmaps(data: RoadmapList):
    roadmaps = data.roadmaps
    
    # Преобразуем каждый Roadmap в словарь с добавленным bayesian_score
    roadmaps_with_scores = [roadmap.dict_with_score() for roadmap in roadmaps]

    # Сортируем по bayesian_score
    sorted_roadmaps = sorted(roadmaps_with_scores, key=lambda x: x["bayesian_score"], reverse=True)

    return {"bayesian_ranking": sorted_roadmaps}
