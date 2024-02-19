from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr


class User(BaseModel):
    email: EmailStr


class UserInDB(User):
    hashed_password: str
