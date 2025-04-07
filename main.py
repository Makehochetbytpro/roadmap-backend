from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal
from sqlalchemy.sql import text
from pydantic import BaseModel
from auth import router as auth_router
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set specific origins like ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allows all headers
)

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

class RoadmapList(BaseModel):
    roadmaps: list[Roadmap]

def bayesian_score(likes: int, dislikes: int, C: float = 0.5, m: int = 50) -> float:
    total_votes = likes + dislikes
    return (likes + C * m) / (total_votes + m)

@app.post("/rank")
def rank_roadmaps(data: RoadmapList):
    roadmaps = data.roadmaps
    
    for roadmap in roadmaps:
        roadmap.bayesian_score = bayesian_score(roadmap.likes, roadmap.dislikes)

    sorted_roadmaps = sorted(roadmaps, key=lambda x: x.bayesian_score, reverse=True)

    return {"bayesian_ranking": sorted_roadmaps}
