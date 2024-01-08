# app/repositories/prompt_repository.py
from datetime import datetime
from typing import Optional, List
from app.database import get_database_connection
from app.models.prompt import Prompt, PromptCreate
from typing import Any
from sqlalchemy import text
from app.repositories.base_repository import BaseRepository


class PromptRepository(BaseRepository):
    def __init__(self):
        super().__init__('prompts')

    def create_prompt(self, prompt_create: Prompt):
        query = text(f"""
            INSERT INTO {self.table_name} (board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number)
            VALUES (:board_id, :prompt_text, :prompt_out, :created_at, :updated_at, :client_number, :customer_number)
            RETURNING id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number;
        """)

        values = {
            "board_id": prompt_create.board_id,
            "prompt_text": prompt_create.prompt_text,
            "prompt_out": prompt_create.prompt_out,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "client_number": prompt_create.client_number,
            "customer_number": prompt_create.customer_number
        }

        created_prompt_tuple = self.execute_query(query, values)
        created_prompt = Prompt(**dict(zip(Prompt.__annotations__, created_prompt_tuple)))
        return created_prompt

    def get_prompts_for_board(self, board_id: int) -> List[Prompt]:
        query = text(f"""
            SELECT id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number
            FROM {self.table_name}
            WHERE board_id = :board_id;
        """)

        values = {"board_id": board_id}

        prompts_data_list = self.execute_query_all(query, values)
        prompts_dict = [Prompt(**dict(zip(Prompt.__annotations__, prompts_data))) for prompts_data in prompts_data_list]
        return prompts_dict

    def get_prompt(self, prompt_id: int) -> Optional[Prompt]:
        query = text(f"""
            SELECT id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number
            FROM {self.table_name}
            WHERE id = :prompt_id;
        """)

        values = {"prompt_id": prompt_id}

        prompt_data = self.execute_query(query, values)

        if prompt_data:
            return Prompt(**dict(zip(Prompt.__annotations__, prompt_data)))
        return None

    def update_prompt(self, prompt_id: int, prompt: PromptCreate) -> Optional[Prompt]:
        query = text(f"""
            UPDATE {self.table_name}
            SET prompt_text = :prompt_text, prompt_out = :prompt_out, updated_at = :updated_at,
                client_number = :client_number, customer_number = :customer_number
            WHERE id = :prompt_id
            RETURNING id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number;
        """)

        values = {
            "prompt_text": prompt.prompt_text,
            "prompt_out": prompt.prompt_out,
            "updated_at": datetime.utcnow(),
            "client_number": prompt.client_number,
            "customer_number": prompt.customer_number,
            "prompt_id": prompt_id
        }

        updated_prompt_data = self.execute_query(query, values)

        if updated_prompt_data:
            return Prompt(**dict(zip(Prompt.__annotations__, updated_prompt_data)))
        return None

    def delete_prompt(self, prompt_id: int) -> Optional[Prompt]:
        query = text(f"""
            DELETE FROM {self.table_name}
            WHERE id = :prompt_id
            RETURNING id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number;
        """)

        values = {"prompt_id": prompt_id}

        deleted_prompt_data = self.execute_query(query, values)

        if deleted_prompt_data:
            return Prompt(**dict(zip(Prompt.__annotations__, deleted_prompt_data)))
        return None