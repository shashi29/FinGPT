# app/repositories/board_repository.py

from typing import Any, Optional
from psycopg2 import sql
from app.repositories.base_repository import BaseRepository
from app.models.board import Board

class BoardRepository(BaseRepository):
    def __init__(self):
        super().__init__('Boards')

    def create_board(self, board: Board) -> Any:
        query = sql.SQL("""
            INSERT INTO Boards (user_id, name, created_at, client_number, customer_number)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, user_id, name, created_at, client_number, customer_number;
        """).format(table_name=sql.Identifier(self.table_name))

        values = (board.user_id, board.name, board.created_at, board.client_number, board.customer_number)

        board_data_tuple = self.execute_query(query, values)
        board_instance = Board(**dict(zip(Board.__annotations__, board_data_tuple)))
        return board_instance

    def get_boards(self) -> Any:
        query = sql.SQL("""
            SELECT * FROM Boards;
        """).format(table_name=sql.Identifier(self.table_name))

        board_data_list = self.execute_query_all(query)
        board_dict = [Board(**dict(zip(Board.__annotations__, board_data))) for board_data in board_data_list]
        return board_dict

    def get_board(self, board_id: int) -> Any:
        query = sql.SQL("""
            SELECT * FROM Boards WHERE id = %s;
        """).format(table_name=sql.Identifier(self.table_name))

        values = (board_id,)

        board_data_tuple = self.execute_query(query, values)
        board_instance = Board(**dict(zip(Board.__annotations__, board_data_tuple)))
        return board_instance

    def update_board(self, board_id: int, board: Board) -> Any:
        query = sql.SQL("""
            UPDATE Boards
            SET name = %s, created_at = %s, client_number = %s, customer_number = %s
            WHERE id = %s
            RETURNING id, user_id, name, created_at, client_number, customer_number;
        """).format(table_name=sql.Identifier(self.table_name))

        values = (board.name, board.created_at, board.client_number, board.customer_number, board_id)
        
        board_data_tuple = self.execute_query(query, values)
        board_instance = Board(**dict(zip(Board.__annotations__, board_data_tuple)))
        return board_instance

    def delete_board(self, board_id: int) -> Any:
        query = sql.SQL("""
            DELETE FROM Boards WHERE id = %s
            RETURNING id, user_id, name, created_at, client_number, customer_number;
        """).format(table_name=sql.Identifier(self.table_name))

        values = (board_id,)

        board_data_tuple = self.execute_query(query, values)
        board_instance = Board(**dict(zip(Board.__annotations__, board_data_tuple)))
        return board_instance
