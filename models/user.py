from pydantic import BaseModel, EmailStr
from typing import Optional
from db.config import db
from typing import Any


class User(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    first_name: str
    last_name: str
    image_url: Optional[str] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.email = self.email.lower()
    @staticmethod
    def init():
        db.users.create_index([("email", 1)], unique=True)


class UserInDB(User):
    hashed_password: str
    is_verified: bool