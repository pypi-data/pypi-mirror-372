from pydantic import BaseModel, EmailStr
from pydantic.dataclasses import dataclass

from .user import User


@dataclass()
class LoginRequest:
    email: EmailStr
    password: str


@dataclass()
class RegisterRequest:
    username: str
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    user: User


class JWTTokens(BaseModel):
    accessToken: str
    refreshToken: str
    refreshTokenJti: str | None = None
