from sqlalchemy.orm import Session
from database import SessionLocal  # сессия из database.py
from models import Category, Topic  # модели

# Открываем сессию
db: Session = SessionLocal()

# 1. Проверяем, существует ли категория
category_name = "Languages"
category = db.query(Category).filter_by(name=category_name).first()

# Если категория не существует, создаём её
if not category:
    category = Category(name=category_name)
    db.add(category)
    db.commit()
    db.refresh(category)

# 2. Создаём топик и привязываем к категории
new_topic = Topic(
    name="Spanish",
    description="Explore Spanish, one of the world’s most spoken languages, with engaging steps that boost your vocabulary, grammar, and speaking skills. Ideal for beginners or those looking to refresh their knowledge.",
    category_id=category.category_id  # используем уже существующую категорию
)
db.add(new_topic)
db.commit()
db.refresh(new_topic)

# 3. Проверяем связи

# Найти категорию и получить её топики
category = db.query(Category).filter_by(name=category_name).first()
print(f"Топики в категории '{category.name}': {[topic.name for topic in category.topics]}")

# Найти топик и получить его категорию
topic = db.query(Topic).filter_by(name="C#").first()
print(f"Категория топика '{topic.name}': {topic.category.name}")

# Закрываем сессию
db.close()
