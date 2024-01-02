# app/repositories/prompt_repository.py
from datetime import datetime
from typing import Optional, List
from app.database import get_database_connection
from app.models.prompt import Prompt, PromptCreate

def create_prompt(db, prompt_create: Prompt):
    query = """
        INSERT INTO Prompts (board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number;
    """
    with db.cursor() as cur:
        cur.execute(query, (
            prompt_create.board_id,
            prompt_create.prompt_text,
            prompt_create.prompt_out,
            datetime.utcnow(),
            datetime.utcnow(),
            prompt_create.client_number,
            prompt_create.customer_number
        ))
        created_prompt_tuple = cur.fetchone()

    db.commit()
    created_prompt = Prompt(**dict(zip(Prompt.__annotations__, created_prompt_tuple)))
    return created_prompt

def get_prompts_for_board(db, board_id: int) -> List[Prompt]:
    query = """
        SELECT id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number
        FROM Prompts
        WHERE board_id = %s;
    """
    with db.cursor() as cur:
        cur.execute(query, (board_id,))
        prompts_data_list = cur.fetchall()

    prompts_dict = [Prompt(**dict(zip(Prompt.__annotations__, prompts_data))) for prompts_data in prompts_data_list]
    return prompts_dict

def get_prompt(db, prompt_id: int) -> Optional[Prompt]:
    query = """
        SELECT id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number
        FROM Prompts
        WHERE id = %s;
    """
    with db.cursor() as cur:
        cur.execute(query, (prompt_id,))
        created_prompt_tuple = cur.fetchone()

    created_prompt = Prompt(**dict(zip(Prompt.__annotations__, created_prompt_tuple)))
    return created_prompt

def update_prompt(db, prompt_id: int, prompt: PromptCreate) -> Optional[Prompt]:
    query = """
        UPDATE Prompts
        SET prompt_text = %s, prompt_out = %s, updated_at = %s, client_number = %s, customer_number = %s
        WHERE id = %s
        RETURNING id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number;
    """
    with db.cursor() as cur:
        cur.execute(query, (
            prompt.prompt_text,
            prompt.prompt_out,
            datetime.utcnow(),
            prompt.client_number,
            prompt.customer_number,
            prompt_id
        ))
        created_prompt_tuple = cur.fetchone()

    db.commit()
    created_prompt = Prompt(**dict(zip(Prompt.__annotations__, created_prompt_tuple)))
    return created_prompt

def delete_prompt(db, prompt_id: int) -> Optional[Prompt]:
    query = """
        DELETE FROM Prompts
        WHERE id = %s
        RETURNING id, board_id, prompt_text, prompt_out, created_at, updated_at, client_number, customer_number;
    """
    with db.cursor() as cur:
        cur.execute(query, (prompt_id,))
        deleted_prompt_tuple = cur.fetchone()

    db.commit()
    deleted_prompt = Prompt(**dict(zip(Prompt.__annotations__, deleted_prompt_tuple)))
    return deleted_prompt
