from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from database import Base
from passlib.context import CryptContext  # type: ignore
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from enum import Enum

class UserRole(Enum):
    USER = 1
    ADMIN = 2


class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(BYTEA, nullable=False)  # Хэшированный пароль
    role = Column(Integer, nullable=False, default=UserRole.USER.value)  # Добавил default user

    roadmaps = relationship("Roadmap", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    comment_likes = relationship("CommentLike", back_populates="user", cascade="all, delete-orphan")
    topic_likes = relationship("TopicLike", back_populates="user", cascade="all, delete-orphan")


    
    # Хэширование пароля
    def set_password(self, password: str):
        self.password = pwd_context.hash(password).encode() #кодируем в bytes

    # Проверка пароля
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password) #обратно преобразуем пароль



class Category(Base):
    __tablename__ = "Category"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    topics = relationship("Topic", back_populates="category", cascade="all, delete-orphan") # хранит список топиков


class Topic(Base):
    __tablename__ = "Topic"

    topic_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    comment = Column(Text)
    topic_likes = relationship("TopicLike", back_populates="topic", cascade="all, delete-orphan")
    like_count = Column(Integer, default=0)
    dislike_count = Column(Integer, default=0)
    image = Column(BYTEA)

    category_id = Column(Integer, ForeignKey("Category.category_id", ondelete="CASCADE"))
    category = relationship("Category", back_populates="topics")

    roadmap = relationship("Roadmap", back_populates="topic", uselist=False)  # Один к одному
    c_roadmaps = relationship("CommunityRoadmap", back_populates="topic")



class Roadmap(Base):
    __tablename__ = "Roadmap"

    roadmap_id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("Topic.topic_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))  # кто создал (например админ)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

    topic = relationship("Topic", back_populates="roadmap")  # Связь с топиком
    user = relationship("User")  # Кто создал
    steps = relationship("Step", back_populates="roadmap", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="roadmap", cascade="all, delete-orphan")

    # community_roadmap өзгергенде оригинальный роадмап озгерген


class CommunityRoadmap(Base):
    __tablename__ = "CommunityRoadmap"

    c_roadmap_id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("Topic.topic_id", ondelete="CASCADE"))
    proposed_steps = Column(Text, nullable=False)  # Текстовая версия предложенных шагов (например, JSON)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)  # Общее количество голосов
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

    topic = relationship("Topic", back_populates="c_roadmaps")
    votes = relationship("Vote", back_populates="community_roadmap", cascade="all, delete-orphan")  # Связь с голосами

    def get_vote_percentage(self):
        if self.total_votes == 0:
            return 0
        return (self.upvotes / self.total_votes) * 100

    def can_apply_changes(self):
        return self.get_vote_percentage() >= 50

    def update_votes(self):
        #Метод для пересчета голосов после каждого нового голосования
        self.upvotes = sum(1 for vote in self.votes if vote.vote_type == "upvote")
        self.downvotes = sum(1 for vote in self.votes if vote.vote_type == "downvote")
        self.total_votes = len(self.votes)



class Vote(Base):
    __tablename__ = "Vote"

    vote_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    c_roadmap_id = Column(Integer, ForeignKey("CommunityRoadmap.c_roadmap_id", ondelete="CASCADE"))
    vote_type = Column(String(10), nullable=False)  # "upvote" или "downvote"

    user = relationship("User", back_populates="votes")
    community_roadmap = relationship("CommunityRoadmap", back_populates="votes")

    __table_args__ = (UniqueConstraint('user_id', 'c_roadmap_id', name='_user_c_roadmap_uc'),)  # Уникальное ограничение


class Step(Base):
    __tablename__ = "Step"

    step_id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("Roadmap.roadmap_id", ondelete="CASCADE"))
    parent_step_id = Column(Integer, ForeignKey("Step.step_id", ondelete="CASCADE"), nullable=True)

    step_order = Column(Integer, default=0)

    step_title = Column(String(255), nullable=False)
    step_description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

    roadmap = relationship("Roadmap", back_populates="steps")
    parent = relationship("Step", remote_side=[step_id], backref="sub_steps")  # связь с родителем и дочерними шагами


class Comment(Base):
    __tablename__ = "Comment"

    comment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    roadmap_id = Column(Integer, ForeignKey("Roadmap.roadmap_id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="comments")
    roadmap = relationship("Roadmap", back_populates="comments")
    comment_likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")


# Модель для лайков/дизлайков топиков
class TopicLike(Base):
    __tablename__ = "topic_likes"

    like_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    topic_id = Column(Integer, ForeignKey("Topic.topic_id", ondelete="CASCADE"))
    is_like = Column(Boolean, default=True)  # True = лайк, False = дизлайк
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="topic_likes")
    topic = relationship("Topic", back_populates="topic_likes")

# Модель для лайков/дизлайков комментариев
class CommentLike(Base):
    __tablename__ = "comment_likes"

    like_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    comment_id = Column(Integer, ForeignKey("Comment.comment_id", ondelete="CASCADE"))
    is_like = Column(Boolean, default=True)  # True = лайк, False = дизлайк
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="comment_likes")
    comment = relationship("Comment", back_populates="comment_likes")