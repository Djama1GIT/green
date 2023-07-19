from sqlalchemy import Column, Integer, String, Boolean, JSON

from db import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, index=True, unique=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    permissions = Column(JSON, nullable=False, default={
        'give_permissions': False,
        'create_accounts': False,
        'add_news': False,
        'edit_news': False,
        'delete_news': False,
    })
