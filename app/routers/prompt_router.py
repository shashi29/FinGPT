# app/routers/prompt_router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.repositories.prompt_repository import PromptRepository
from app.models.prompt import Prompt, PromptCreate
from app.database import get_database_connection

router = APIRouter(prefix="/prompts", tags=["Prompts"])

prompt_repository = PromptRepository()

@router.post("/", response_model=Prompt)
def create_prompt_route(prompt_create: Prompt):
    new_prompt = prompt_repository.create_prompt(prompt_create)
    return new_prompt

@router.get("/boards/{board_id}", response_model=List[Prompt])
def get_prompts_for_board_route(board_id: int):
    prompts = prompt_repository.get_prompts_for_board(board_id)
    return prompts

@router.get("/{prompt_id}", response_model=Prompt)
def get_prompt_route(prompt_id: int):
    prompt = prompt_repository.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.put("/{prompt_id}", response_model=Prompt)
def update_prompt_route(prompt_id: int, prompt: PromptCreate):
    updated_prompt = prompt_repository.update_prompt(prompt_id, prompt)
    if not updated_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt

@router.delete("/{prompt_id}", response_model=Prompt)
def delete_prompt_route(prompt_id: int):
    deleted_prompt = prompt_repository.delete_prompt(prompt_id)
    if not deleted_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return deleted_prompt
