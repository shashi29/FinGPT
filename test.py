import psycopg2
import logging
import json

from configparser import ConfigParser
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from typing import Optional, Any, List

app = FastAPI()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "test_token"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

class UserLogin(BaseModel):
    email: str
    password: str

class Board(BaseModel):
    name: str
    user_id: Optional[Any]
    created_at: Optional[datetime] = None
    client_number: Optional[str] = None
    customer_number: Optional[str] = None

def get_database_connection():
    config = ConfigParser()
    config.read('config.ini')
    db_config = config['database']

    conn = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )

    return conn

class PromptCreate(BaseModel):
    prompt_text: str
    client_number: Optional[str] = None
    customer_number: Optional[str] = None

class PromptUpdate(BaseModel):
    prompt_text: str
    client_number: Optional[str] = None
    customer_number: Optional[str] = None

class Prompt(BaseModel):
    #id: int
    #board_id: int
    board_name: str
    prompt_text: str
    prompt_out: str
    client_number: Optional[str] = None
    customer_number: Optional[str] = None
    created_at : Optional[str] = None
    updated_at : Optional[str] = None

def get_all_prompts_for_board(conn, cursor, board_id: int) -> List[Prompt]:
    # Define the SQL query with placeholders for values
    query = sql.SQL("""
        SELECT * FROM prompts WHERE board_id = %s;
    """)

    # Execute the query with the provided values
    cursor.execute(query, (board_id,))

    # Fetch all the rows as dictionaries
    prompts_data = cursor.fetchall()

    # Convert the rows to Prompt objects
    prompts = [Prompt(**prompt) for prompt in prompts_data]

    return prompts

def get_board_id(db, board_name):
    cur = db.cursor()
    cur.execute("SELECT id FROM Boards WHERE name = %s", (board_name,))
    return cur.fetchone()

def create_prompt(db, board_id, prompt):
    cur = db.cursor()
    if prompt.created_at is None:
        prompt.created_at = datetime.now().isoformat()

    # Define the SQL query with placeholders for values
    query = """
        INSERT INTO prompts (board_id, board_name, prompt_text, prompt_out, client_number, customer_number, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING board_id, board_name, prompt_text, prompt_out, client_number, customer_number, created_at, updated_at;
    """
    
    # Execute the query with the provided values
    cur.execute(query, (
        board_id,
        prompt.board_name,
        prompt.prompt_text,
        prompt.prompt_out,
        prompt.client_number,
        prompt.customer_number,
        prompt.created_at,
        datetime.utcnow().isoformat()
    ))

    # Fetch the inserted row
    new_prompt = cursor.fetchone()

    # Commit the transaction
    db.commit()

    return new_prompt

@app.get("/api/boards/{board_id}/prompts", response_model=List[Prompt])
def get_prompts_for_board(board_id: int, db = Depends(get_database_connection)):
    board = get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    prompts = get_all_prompts_for_board(db, board_id)
    return prompts

@app.post("/api/boards/{board_name}/prompts", response_model=Prompt)
def save_new_prompt(board_name: str, prompt_create: Prompt, db = Depends(get_database_connection)):
    board_id = get_board_id(db, board_name)
    if not board_id:
        raise HTTPException(status_code=404, detail="Board not found")
    
    new_prompt = create_prompt(db, board_id, prompt_create)
    return new_prompt

@app.put("/api/prompts/{prompt_id}", response_model=Prompt)
def update_prompt_route(prompt_id: int, prompt_update: PromptUpdate, db = Depends(get_database_connection)):
    existing_prompt = get_prompt(db, prompt_id)
    if not existing_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    updated_prompt = update_prompt(db, prompt_id, prompt_update)
    return updated_prompt

@app.delete("/api/prompts/{prompt_id}", response_model=dict)
def delete_prompt_route(prompt_id: int, db = Depends(get_database_connection)):
    deleted = delete_prompt(db, prompt_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"status": "Prompt deleted successfully"}

@app.post("/api/boards/{board_id}/generate", response_model=dict)
def execute_prompt_on_board_documents(board_id: int, db = Depends(get_database_connection)):
    board = get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Assuming generate_insight is a function to execute prompts on board documents
    result = generate_insight(db, board_id)
    return result

# Run the FastAPI app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
