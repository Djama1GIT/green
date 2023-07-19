from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    permissions: dict
