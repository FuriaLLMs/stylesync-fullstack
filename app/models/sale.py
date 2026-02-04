from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Sale(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    sale_date: datetime
    product_id: str # Alterado para str para suportar ObjectId do MongoDB
    quantity: int
    total_value: float

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
