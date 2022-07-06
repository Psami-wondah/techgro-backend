from pydantic import BaseModel
from models.user import User
from typing import Any

class UserReg(User):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.email = self.email.lower()


class RegRes(BaseModel):
    message: str


class LoginRes(BaseModel):
    message: str
    user: User
    access_token: str


class ResetPassword(BaseModel):
    password: str

class GoogleAuth(BaseModel):
    credential: str