from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash

class LoginPayload(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    password_hash: str
    role: str = "user"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserDBModel(User):
    id: Optional[str] = Field(None, alias="_id")
