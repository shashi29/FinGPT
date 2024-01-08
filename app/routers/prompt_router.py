# app/routers/prompt_router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.repositories.prompt_repository import (
    create_prompt,
    get_prompts_for_board,
    get_prompt,
    update_prompt,
    delete_prompt,
)
from app.models.prompt import Prompt, PromptCreate
from app.database import get_database_connection

router = APIRouter(prefix="/prompts", tags=["Prompts"])

@router.post("/", response_model=Prompt)
def create_prompt_route(prompt_create: Prompt, db=Depends(get_database_connection)):
    new_prompt = create_prompt(db, prompt_create)
    return new_prompt

@router.get("/boards/{board_id}", response_model=List[Prompt])
def get_prompts_for_board_route(board_id: int, db=Depends(get_database_connection)):
    prompts = get_prompts_for_board(db, board_id)
    return prompts

@router.get("/{prompt_id}", response_model=Prompt)
def get_prompt_route(prompt_id: int, db=Depends(get_database_connection)):
    prompt = get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.put("/{prompt_id}", response_model=Prompt)
def update_prompt_route(prompt_id: int, prompt: PromptCreate, db=Depends(get_database_connection)):
    updated_prompt = update_prompt(db, prompt_id, prompt)
    if not updated_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt

@router.delete("/{prompt_id}", response_model=Prompt)
def delete_prompt_route(prompt_id: int, db=Depends(get_database_connection)):
    deleted_prompt = delete_prompt(db, prompt_id)
    if not deleted_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return deleted_prompt
