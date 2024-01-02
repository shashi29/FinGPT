# app/models/board.py
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class Board(BaseModel):
    id: Optional[Any] = None
    user_id: Optional[Any]
    name: str
    created_at: Optional[datetime] = None
    client_number: Optional[str] = None
    customer_number: Optional[str] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "examples": [
                {
                    "name": "Board1",
                    "user_id": "06"
                }
            ]
        }
