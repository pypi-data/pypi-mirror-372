from pydantic import BaseModel, EmailStr

from enum import Enum


class Role(str, Enum):
    Admin = "Admin"
    User = "User"


class User(BaseModel):
    # id: str | None = Field(None, alias="_id")
    _id: str | None
    username: str
    email: EmailStr
    role: Role
    isPremium: bool
    accountLocked: bool
