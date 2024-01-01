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

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_board(db, board: Board):
    #This part is to fill the placeholder in case only name is given
    if board.created_at is None:
        board.created_at = datetime.now().isoformat()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO Boards (user_id, name, created_at, client_number, customer_number) VALUES (%s, %s, %s, %s, %s) RETURNING user_id, name, created_at, client_number, customer_number",
        (board.user_id, board.name, board.created_at, board.client_number, board.customer_number),
    )
    created_board = cur.fetchone()
    db.commit()
    return created_board

def get_boards(db):
    cur = db.cursor()
    cur.execute("SELECT * FROM Boards")
    return cur.fetchall()

def get_board(db, name: str):
    cur = db.cursor()
    cur.execute("SELECT * FROM Boards WHERE name = %s", (name,))
    return cur.fetchall()

def update_board(db, name: str, board: Board):
    cur = db.cursor()
    cur.execute(
        "UPDATE Boards SET name = %s, created_at = %s, client_number = %s, customer_number = %s WHERE name = %s RETURNING id, name, created_at, client_number, customer_number",
        (board.name, board.created_at, board.client_number, board.customer_number, name),
    )
    updated_board = cur.fetchone()
    db.commit()
    return updated_board

def delete_board(db, name: str):
    cur = db.cursor()
    cur.execute("DELETE FROM Boards WHERE name = %s RETURNING id, name, created_at, client_number, customer_number", (name,))
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

@app.get("/boards/{board_name}", response_model=list[Board])
def get_board_route(board_name: str, db=Depends(get_database_connection)):
    boards_data = get_board(db, board_name)
    if not boards_data:
        raise HTTPException(status_code=404, detail="Board not found")
    boards = [
        Board(id=board[0], name=board[2], user_id=board[1], created_at=board[3], client_number=board[4], customer_number=board[5])
        for board in boards_data
    ]
    return boards

#This need to be fix
# @app.put("/boards/{board_name}", response_model=Board)
# def update_board_route(board_id: int, board: Board, db=Depends(get_database_connection)):
#     updated_board = update_board(db, board_id, board)
#     if not updated_board:
#         raise HTTPException(status_code=404, detail="Board not found")
#     boards = [
#         Board(id=updated_board[0], name=updated_board[2], user_id=updated_board[1], created_at=updated_board[3], client_number=updated_board[4], customer_number=updated_board[5])
#     ]
#     return boards

@app.delete("/boards/{board_name}", response_model=dict)
def delete_board_route(board_name: str, db=Depends(get_database_connection)):
    deleted_board = delete_board(db, board_name)
    if not deleted_board:
        raise HTTPException(status_code=404, detail="Board not found")
    return {
        "status_code":200, 
        "detail":"Board deleted sucessfully"
    }


@app.post("/login")
def login(user_data: UserLogin):
    conn = get_database_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE email = %s AND password = %s", (user_data.email, user_data.password))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Token expiration time is set to 24 hours
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_data.email}, expires_delta=expires_delta)

    return {"access_token": access_token, "token_type": "bearer"}

# Run the FastAPI app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
