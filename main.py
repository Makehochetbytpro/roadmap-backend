from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from sqlalchemy.sql import text
from pydantic import BaseModel
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

# Эндпоинт для проверки, какие таблицы есть в базе
@app.get("/check_tables")
def check_tables(db: Session = Depends(get_db)):  # Передаём сессию через Depends
    tables = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).fetchall()
    return {"tables": [table[0] for table in tables]}

# Модель данных для запроса
class CategoryCreate(BaseModel):
    name: str

# Эндпоинт для создания категории
@app.post("/create_category")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db.execute(text('INSERT INTO "Category" (name) VALUES (:name)'), {"name": category.name})
    db.commit()
    return {"message": "Category created successfully", "category": category.name}


