from datetime import date
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    gender: str | None = None
    birth_date: date | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    gender: str | None = None
    birth_date: date | None = None


class UserOut(BaseModel):
    id: str
    openid: str | None = None
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
