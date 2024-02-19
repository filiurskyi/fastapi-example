from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreateSchema(BaseModel):
    email: EmailStr
    passwd: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserViewSchema(UserCreateSchema):
    id: int
    created_at: datetime
    modified_at: datetime
