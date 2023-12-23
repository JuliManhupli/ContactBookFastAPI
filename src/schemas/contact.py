from datetime import date, datetime

from pydantic import BaseModel, Field, EmailStr

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    name: str = Field(max_length=150)
    surname: str = Field(max_length=150)
    email: EmailStr
    phone: str
    birthday: date


class ContactUpdate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None

    class Config:
        from_attributes = True
