from sqlalchemy.orm import Session
from models import Roadmap, Category, User
from database import SessionLocal
import datetime

db: Session = SessionLocal()

category = db.query(Category).filter(Category.name == "Information Technology").first()
user = db.query(User).filter(User.username == "Aibar").first()

if not category or not user:
    print("Категория или пользователь не найдены!")
else:
    new_roadmap = Roadmap(
        title="Introduction to Backend for beginners",
        description="Backend development for beginners. You will learn backend in Python,Flask,PostgreSQL stack",
        category_id=category.category_id,
        user_id=user.user_id,
        created_at=datetime.datetime.utcnow()
    )

    db.add(new_roadmap)
    db.commit()
    db.refresh(new_roadmap)
    db.close()

    print("Роадмап успешно добавлен!")

