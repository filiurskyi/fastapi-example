from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class ContactCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    birth_date: date


class ContactViewSchema(ContactCreateSchema):
    id: int
    created_by: int
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True


class ContactEditSchema(ContactCreateSchema):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    birth_date: date | None = None
