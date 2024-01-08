# app/repositories/board_repository.py

from typing import Any
from sqlalchemy import text
from app.repositories.base_repository import BaseRepository
from app.models.board import Board

class BoardRepository(BaseRepository):
    def __init__(self):
        super().__init__('Boards')

    def create_board(self, board: Board) -> Any:
        query = text("""
            INSERT INTO Boards (user_id, name, created_at, client_number, customer_number)
            VALUES (:user_id, :name, :created_at, :client_number, :customer_number)
            RETURNING id, user_id, name, created_at, client_number, customer_number;
        """)

        values = {
            "user_id": board.user_id,
            "name": board.name,
            "created_at": board.created_at,
            "client_number": board.client_number,
            "customer_number": board.customer_number
        }

        board_data_tuple = self.execute_query(query, values)
        board_instance = Board(**dict(zip(Board.__annotations__, board_data_tuple)))
        return board_instance

    def get_boards(self) -> Any:
        query = text("""
            SELECT * FROM Boards;
        """)

        board_data_list = self.execute_query_all(query)
        board_dict = [Board(**dict(zip(Board.__annotations__, board_data))) for board_data in board_data_list]
        return board_dict

    def get_board(self, board_id: int) -> Any:
        query = text("""
            SELECT * FROM Boards WHERE id = :board_id;
        """)

        values = {"board_id": board_id}

        board_data_tuple = self.execute_query(query, values)
        board_instance = Board(**dict(zip(Board.__annotations__, board_data_tuple)))
        return board_instance

    def update_board(self, board_id: int, board: Board) -> Any:
        query = text("""
            UPDATE Boards
            SET name = :name, created_at = :created_at,
                client_number = :client_number, customer_number = :customer_number
            WHERE id = :board_id
            RETURNING id, user_id, name, created_at, client_number, customer_number;
        """)

        values = {
            "name": board.name,
            "created_at": board.created_at,
            "client_number": board.client_number,
            "customer_number": board.customer_number,
            "board_id": board_id
        }

        board_data_tuple = self.execute_query(query, values)
        board_instance = Board(**dict(zip(Board.__annotations__, board_data_tuple)))
        return board_instance

    def delete_board(self, board_id: int) -> Any:
        query = text("""
            DELETE FROM Boards WHERE id = :board_id
            RETURNING id, user_id, name, created_at, client_number, customer_number;
        """)

        values = {"board_id": board_id}

        board_data_tuple = self.execute_query(query, values)
        board_instance = Board(**dict(zip(Board.__annotations__, board_data_tuple)))
        return board_instance
