from pydantic import BaseModel
from typing import Optional, Any
import uuid

class Order(BaseModel):
    id: str = uuid.uuid4()
    metadata: dict[str, Any] = {}
    product_id: str
    user_id: str
