from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: str
    email: EmailStr

class User(BaseModel):
    id_user: Optional[str] = Field(default=None, alias="_id")  # MongoDB _id es string
    name: str
    email: EmailStr

    class Config:
        validate_by_name = True  # para usar alias _id como id_user
        from_attributes = True