from datetime import date
from pydantic import BaseModel


class RegisterIn(BaseModel):
    nickname: str
    password: str


class LoginIn(BaseModel):
    nickname: str
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    gender: str | None = None
    birth_date: date | None = None


class UserOut(BaseModel):
    id: str
    nickname: str | None = None
    name: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    free_readings_used: int = 0

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
