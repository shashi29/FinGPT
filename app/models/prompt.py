# app/models/prompt.py
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class PromptBase(BaseModel):
    prompt_text: str
    prompt_out: str
    client_number: Optional[str] = None
    customer_number: Optional[str] = None

class PromptCreate(PromptBase):
    pass

class Prompt(BaseModel):
    id: Optional[int] = None
    board_id: int
    prompt_text: str
    prompt_out: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    client_number: Optional[str] = None
    customer_number: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [
                {
                "board_id": 17,
                "prompt_text": "test string",
                "prompt_out": "out string"
                }
            ]
        }
        

