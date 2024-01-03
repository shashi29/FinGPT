import psycopg2
import logging
import logging.config
from datetime import datetime, timedelta

from configparser import ConfigParser
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, Any
from fastapi.responses import JSONResponse

app = FastAPI()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "test_token"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

class UserLogin(BaseModel):
    email: str
    password: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "test@example.com",
                    "password": "admin"
                }
            ]
        }
    }

class Board(BaseModel):
    id:Optional[Any] = None
    name: str
    user_id: Optional[Any]
    created_at: Optional[datetime] = None
    client_number: Optional[str] = None
    customer_number: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Board1",
                    "user_id": "06"
                }
            ]
        }
    }

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

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_board(db, board: Board):
    """
    Create a new board in the database.

    If values for created_at, client_number, or customer_number are not provided,
    default values will be used:
    - created_at: current timestamp
    - client_number: '01'
    - customer_number: '12345'

    :param db: Database connection
    :param board: Board object containing user_id, name, created_at, client_number, and customer_number
    :return: Created board details (user_id, name, created_at, client_number, customer_number)

    To do:
    Add condition to check if board is already exist or not.
    """

    # Set default values if not provided
    board.created_at = board.created_at or datetime.now().isoformat()
    board.client_number = board.client_number or '01'
    board.customer_number = board.customer_number or '12345'

    # Define the SQL query
    query = """
        INSERT INTO Boards (user_id, name, created_at, client_number, customer_number)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING user_id, name, created_at, client_number, customer_number;
    """
    
    # Execute the SQL query
    with db.cursor() as cur:
        cur.execute(query, (
            board.user_id,
            board.name,
            board.created_at,
            board.client_number,
            board.customer_number
        ))

        created_board = cur.fetchone()

    db.commit()
    return created_board


def get_boards(db):
    cur = db.cursor()
    cur.execute("SELECT * FROM Boards")
    return cur.fetchall()

def get_board(db, board_id: int):
    cur = db.cursor()
    cur.execute("SELECT * FROM Boards WHERE id = %s", (board_id,))
    return cur.fetchall()

def update_board(db, board_id: int, board: Board):
    cur = db.cursor()
    cur.execute(
        "UPDATE Boards SET name = %s, created_at = %s, client_number = %s, customer_number = %s WHERE id = %s RETURNING id, name, created_at, client_number, customer_number",
        (board.name, board.created_at, board.client_number, board.customer_number, board_id),
    )
    updated_board = cur.fetchone()
    db.commit()
    return updated_board

def delete_board(db, board_id: int):
    cur = db.cursor()
    cur.execute("DELETE FROM Boards WHERE id = %s RETURNING id, name, created_at, client_number, customer_number", (board_id,))
    deleted_board = cur.fetchone()
    db.commit()
    return deleted_board

@app.post("/boards/", response_model=Board)
def create_board_route(board: Board, db=Depends(get_database_connection)):
    created_board = create_board(db, board)
    return board

@app.get("/boards/", response_model=list[Board])
def get_boards_route(db=Depends(get_database_connection)):
    boards_data = get_boards(db)
    boards = [
        Board(id=board[0], name=board[2], user_id=board[1], created_at=board[3], client_number=board[4], customer_number=board[5])
        for board in boards_data
    ]
    return boards

@app.get("/boards/{board_id}", response_model=Board)
def get_board_route(board_id: int, db=Depends(get_database_connection)):
    boards_data = get_board(db, board_id)
    if not boards_data:
        raise HTTPException(status_code=404, detail="Board not found")
    boards = [
        Board(id=board[0], name=board[2], user_id=board[1], created_at=board[3], client_number=board[4], customer_number=board[5])
        for board in boards_data
    ]
    return boards

#This need to be fix
@app.put("/boards/{board_id}", response_model=dict)
def update_board_route(board_id: int, board: Board, db=Depends(get_database_connection)):
    updated_board = update_board(db, board_id, board)
    if not updated_board:
        raise HTTPException(status_code=404, detail="Board not found")
    keys = ['id', 'name', 'user_id', 'created_at', 'client_number', 'customer_number']

    # Create a dictionary using the keys and values from the tuple
    board_dict = dict(zip(keys, updated_board))
    return board_dict

@app.delete("/boards/{board_id}", response_model=dict)
def delete_board_route(board_id: int, db=Depends(get_database_connection)):
    deleted_board = delete_board(db, board_id)
    if not deleted_board:
        raise HTTPException(status_code=404, detail="Board not found")
    response_data = {
        "status_code":200, 
        "detail":"Board deleted sucessfully"
    }
    return JSONResponse(content=response_data)


@app.post("/login", response_model=dict)
def login(user_data: UserLogin, db=Depends(get_database_connection)):
    cur = db.cursor()
    cur.execute("SELECT * FROM Users WHERE email = %s AND password = %s", (user_data.email, user_data.password))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Token expiration time is set to 24 hours
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_data.email}, expires_delta=expires_delta)

    response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user[0],
            "user_name": user[1],
            "email": user[2],
            # Add other user details as needed
        }

    return JSONResponse(content=response_data)

# Run the FastAPI app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
