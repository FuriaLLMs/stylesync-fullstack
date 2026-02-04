from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    name: str
    description: Optional[str] = None
