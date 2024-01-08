# app/routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.repositories.user_repository import UserRepository, create_access_token
from app.models.user import User
from app.database import get_database_connection
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from app.exceptions import UserNotFoundException, EmailAlreadyInUseException, InternalServerErrorException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

router = APIRouter(prefix="/users", tags=["Users"])

user_repository = UserRepository()

@router.post("/", response_model=User)
async def create_user(user: User):
    # try:
    created_user = user_repository.create_user(user)
    return created_user
    # except Exception as e:
    #     raise InternalServerErrorException from e

@router.get("/", response_model=List[User])
async def get_users():
    users = user_repository.get_users()
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = user_repository.get_user(user_id)
    if not user:
        raise UserNotFoundException
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
#    try:
    updated_user = user_repository.update_user(user_id, user)
    if not updated_user:
        raise UserNotFoundException
    return updated_user
    # except IntegrityError:
    #     raise EmailAlreadyInUseException
    # except Exception as e:
    #     raise InternalServerErrorException from e

@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    try:
        deleted_user = user_repository.delete_user(user_id)
        if not deleted_user:
            raise UserNotFoundException
        response_data = {"status_code": 200, "detail": "User deleted successfully"}
        return response_data
    except Exception as e:
        raise InternalServerErrorException from e

@router.post("/login", response_model=dict)
def login(user_data: User):
    # try:
    #cur = db.connect()
    #cur.execute("SELECT * FROM Users WHERE email = %s AND password = %s", {"email":user_data.email, "password":user_data.password})
    user = user_repository.login_user(user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_data.email}, expires_delta=expires_delta)

    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "user_name": user.name,
        "email": user.email,
        # Add other user details as needed
    }

    return JSONResponse(content=response_data)
    # except Exception as e:
    #     raise InternalServerErrorException from e
