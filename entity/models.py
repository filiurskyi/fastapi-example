from datetime import date, datetime, timezone

from pydantic import EmailStr
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(
        Integer(), primary_key=True, unique=True, autoincrement=True
    )
    first_name: Mapped[str] = mapped_column(String(40), nullable=True)
    last_name: Mapped[str] = mapped_column(String(45), nullable=True)
    email: Mapped[EmailStr] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date)
    #  maybe some extras
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, default=1
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
    )


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        Integer(), primary_key=True, unique=True, autoincrement=True
    )
    email: Mapped[EmailStr] = mapped_column(String(50))
    passwd: Mapped[str] = mapped_column(String(80))
    salt: Mapped[str] = mapped_column(String(65), default="Default_salt")
    is_active: Mapped[bool] = mapped_column(default=False)
    otp: Mapped[int] = mapped_column(nullable=True, default=None)
    image: Mapped[str] = mapped_column(String(255), default=None, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
    )
