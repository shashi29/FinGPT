from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import timedelta
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.repositories.user_repository import UserRepository, create_access_token
from app.exceptions import UserNotFoundException, EmailAlreadyInUseException, InternalServerErrorException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

router = APIRouter(prefix="/users", tags=["Users"])
user_repository = UserRepository()

@router.post("/", response_model=User)
async def create_user(user: User):
    try:
        created_user = user_repository.create_user(user)
        return created_user
    except EmailAlreadyInUseException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use")
    except InternalServerErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[User])
async def get_users():
    users = user_repository.get_users()
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    try:
        user = user_repository.get_user(user_id)
        if not user:
            raise UserNotFoundException
        return user
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    try:
        updated_user = user_repository.update_user(user_id, user)
        if not updated_user:
            raise UserNotFoundException
        return updated_user
    except EmailAlreadyInUseException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use")
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except InternalServerErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    try:
        deleted_user = user_repository.delete_user(user_id)
        if not deleted_user:
            raise UserNotFoundException
        response_data = {"status_code": 200, "detail": "User deleted successfully"}
        return response_data
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except InternalServerErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/login", response_model=dict)
def login(user_data: User):
    try:
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
    except HTTPException as e:
        raise e
    except InternalServerErrorException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
