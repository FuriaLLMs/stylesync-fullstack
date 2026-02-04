from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
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
    # Aceita qualquer tipo (incluindo ObjectId) vindo do alias _id
    id: Optional[Any] = Field(None, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
