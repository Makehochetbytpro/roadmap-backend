from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from database import Base
from passlib.context import CryptContext  # type: ignore
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Хэшированный пароль
    role = Column(String(45), nullable=False)

    roadmaps = relationship("Roadmap", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")

    # Хэширование пароля
    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    # Проверка пароля
    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password)


class Category(Base):
    __tablename__ = "Category"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    roadmaps = relationship("Roadmap", back_populates="category")


class Roadmap(Base):
    __tablename__ = "Roadmap"

    roadmap_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("Category.category_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

    category = relationship("Category", back_populates="roadmaps")
    user = relationship("User", back_populates="roadmaps")
    steps = relationship("Step", back_populates="roadmap")
    comments = relationship("Comment", back_populates="roadmap")
    likes = relationship("Like", back_populates="roadmap")


class Step(Base):
    __tablename__ = "Step"

    step_id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("Roadmap.roadmap_id", ondelete="CASCADE"))
    step_title = Column(String(255), nullable=False)
    step_description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

    roadmap = relationship("Roadmap", back_populates="steps")


class Comment(Base):
    __tablename__ = "Comment"

    comment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    roadmap_id = Column(Integer, ForeignKey("Roadmap.roadmap_id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="comments")
    roadmap = relationship("Roadmap", back_populates="comments")


class Like(Base):
    __tablename__ = "Like"

    like_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    roadmap_id = Column(Integer, ForeignKey("Roadmap.roadmap_id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="likes")
    roadmap = relationship("Roadmap", back_populates="likes")

    __table_args__ = (UniqueConstraint("user_id", "roadmap_id", name="unique_like"),)
