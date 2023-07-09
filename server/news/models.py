from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship("User")
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    content = Column(String)
    views = Column(Integer, default=0)

    def json(self):
        return {
            'id': self.id,
            'author_id': self.author_id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'views': self.views,
        }
