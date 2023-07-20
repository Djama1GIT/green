import hashlib

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship
from db import Base

from datetime import datetime


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship("User")
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    content = Column(String)
    views = Column(Integer, default=0)
    time = Column(DateTime, default=datetime.utcnow())
    category = Column(String, ForeignKey('categories.name', ondelete='CASCADE'), default="IT", nullable=False)

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'views': self.views,
            'time': str(self.time),
            'category': self.category
        }


class Follower(Base):
    __tablename__ = 'follower'

    uuid = Column(UUID, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True, unique=True)
    token = Column(String, nullable=False, index=True)

    @staticmethod
    def generate_token(uuid, email):
        data = f"{uuid}+{email}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()
