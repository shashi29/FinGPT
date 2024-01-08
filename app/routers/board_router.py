# app/routers/board_router.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.repositories.board_repository import BoardRepository
from app.models.board import Board

router = APIRouter(prefix="/boards", tags=["Boards"])

board_repository = BoardRepository()

@router.post("/", response_model=Board)
async def create_board(board: Board):
    created_board = board_repository.create_board(board)
    return created_board

@router.get("/", response_model=List[Board])
async def get_boards():
    boards = board_repository.get_boards()
    return boards

@router.get("/{board_id}", response_model=Board)
async def get_board(board_id: int):
    board = board_repository.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.put("/{board_id}", response_model=Board)
async def update_board(board_id: int, board: Board):
    updated_board = board_repository.update_board(board_id, board)
    if not updated_board:
        raise HTTPException(status_code=404, detail="Board not found")
    return updated_board

@router.delete("/{board_id}", response_model=dict)
async def delete_board(board_id: int):
    deleted_board = board_repository.delete_board(board_id)
    if not deleted_board:
        raise HTTPException(status_code=404, detail="Board not found")
    response_data = {"status_code": 200, "detail": "Board deleted successfully"}
    return response_data
