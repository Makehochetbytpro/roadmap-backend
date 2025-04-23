import datetime
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pydantic import BaseModel
from typing import List
from database import SessionLocal
from models import Topic, Roadmap, User, Step, Comment, CommentLike, TopicLike
from schemas import RoadmapCreateRequest, StepCreateRequest, StepResponse, CommentCreate, CommentResponse
from auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from auth import get_current_user

app = FastAPI()
app.include_router(auth_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class RoadmapListRequest(BaseModel):
    roadmaps: List[RoadmapScoreModel]

@app.post("/rank")
def rank_roadmaps(data: RoadmapListRequest):
    roadmaps_with_scores = [roadmap.dict_with_score() for roadmap in data.roadmaps]
    sorted_roadmaps = sorted(roadmaps_with_scores, key=lambda x: x["bayesian_score"], reverse=True)
    return {"bayesian_ranking": sorted_roadmaps}

# ========================== ЛАЙКИ НА ТОПИК ==========================

@app.post("/topics/{topic_id}/like")
def like_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic.like_count += 1
    db.commit()
    return {"message": "Liked!", "like_count": topic.like_count}

@app.post("/topics/{topic_id}/dislike")
def dislike_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.topic_id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic.dislike_count += 1
    db.commit()
    return {"message": "Disliked!", "dislike_count": topic.dislike_count}

# ========================== РОАДМАПЫ ==========================

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

@app.get("/roadmap/{roadmap_id}", response_model=list[StepResponse])
def get_steps_by_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    steps = db.query(Step).filter(Step.roadmap_id == roadmap_id).order_by(Step.step_order).all()
    return steps

# =========================== КОММЕНТАРИИ ===========================


@app.post("/comments/", response_model=CommentResponse)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    parent_comment_id = comment.parent_comment_id if comment.parent_comment_id else None

    new_comment = Comment(
        user_id=current_user.user_id,
        topic_id=comment.topic_id,
        parent_comment_id=parent_comment_id,
        content=comment.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@app.get("/comments/topic/{topic_id}", response_model=List[CommentResponse])
def get_comments_by_topic(topic_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.topic_id == topic_id).all()
    return comments

@app.get("/comments/{comment_id}/replies", response_model=List[CommentResponse])
def get_replies(comment_id: int, db: Session = Depends(get_db)):
    replies = db.query(Comment).filter(Comment.parent_comment_id == comment_id).all()
    return replies

# =========================== ДЕРЕВО КОММЕНТАРИЕВ ===========================

def get_comment_likes_count(db: Session, comment_id: int):
    likes = db.query(CommentLike).filter(CommentLike.comment_id == comment_id, CommentLike.is_like == True).count()
    dislikes = db.query(CommentLike).filter(CommentLike.comment_id == comment_id, CommentLike.is_like == False).count()
    return likes, dislikes

def build_comment_tree(comments, db):
    comment_dict = {comment.comment_id: comment for comment in comments}
    tree = []

    def serialize(comment):
        likes, dislikes = get_comment_likes_count(db, comment.comment_id)
        return {
            "comment_id": comment.comment_id,
            "user_id": comment.user_id,
            "text": comment.content,
            "date": comment.created_at.strftime("%Y-%m-%d"),
            "edited": comment.edited,
            "likes": likes,
            "dislikes": dislikes,
            "parent_id": comment.parent_comment_id or None,
            "reply": []
        }

    comment_data = {c.comment_id: serialize(c) for c in comments}

    for comment in comments:
        if comment.parent_comment_id:
            parent = comment_data.get(comment.parent_comment_id)
            if parent:
                parent["reply"].append(comment_data[comment.comment_id])
        else:
            tree.append(comment_data[comment.comment_id])

    return tree

@app.get("/comments/{topic_id}")
def get_comments(topic_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.topic_id == topic_id).order_by(Comment.created_at).all()
    return build_comment_tree(comments, db)

# =========================== ЛАЙКИ ТОПИКОВ ===========================

@app.post("/topics/{topic_id}/like")
def like_topic(topic_id: int, is_like: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    topic_like = db.query(TopicLike).filter_by(user_id=current_user.user_id, topic_id=topic_id).first()
    if topic_like:
        topic_like.is_like = is_like  # Обновляем лайк/дизлайк
    else:
        topic_like = TopicLike(user_id=current_user.user_id, topic_id=topic_id, is_like=is_like)
        db.add(topic_like)

    db.commit()
    return {"message": "Лайк/дизлайк темы успешно сохранён."}


@app.get("/topics/{topic_id}/likes")
def get_topic_likes(topic_id: int, db: Session = Depends(get_db)):
    likes = db.query(TopicLike).filter_by(topic_id=topic_id, is_like=True).count()
    dislikes = db.query(TopicLike).filter_by(topic_id=topic_id, is_like=False).count()
    return {"likes": likes, "dislikes": dislikes}

# =========================== ЛАЙКИ КОММЕНТАРИЕВ ===========================

@app.post("/comments/{comment_id}/like")
def like_comment(comment_id: int, is_like: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment_like = db.query(CommentLike).filter_by(user_id=current_user.user_id, comment_id=comment_id).first()
    if comment_like:
        comment_like.is_like = is_like  # Обновляем лайк/дизлайк
    else:
        comment_like = CommentLike(user_id=current_user.user_id, comment_id=comment_id, is_like=is_like)
        db.add(comment_like)

    db.commit()
    return {"message": "Лайк/дизлайк комментария успешно сохранён."}


@app.get("/comments/{comment_id}/likes")
def get_comment_likes(comment_id: int, db: Session = Depends(get_db)):
    likes = db.query(CommentLike).filter_by(comment_id=comment_id, is_like=True).count()
    dislikes = db.query(CommentLike).filter_by(comment_id=comment_id, is_like=False).count()
    return {"likes": likes, "dislikes": dislikes}
