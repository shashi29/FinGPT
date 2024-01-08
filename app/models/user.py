# app/models/user.py

from typing import Optional, Any
from pydantic import BaseModel

class User(BaseModel):
    id: Optional[Any] = None
    name: Optional[str] = None
    email: str
    password: str
    client_number: Optional[str] = None
    customer_number: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name" : "test",
                    "email": "test@example.com",
                    "password": "admin",
                    "client_number" : "01",
                    "customer_number" : "12345"
                }
            ]
        }
    }
