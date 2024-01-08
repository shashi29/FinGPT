# app/repositories/user_repository.py

from typing import Any, Optional
from psycopg2 import sql
from app.repositories.base_repository import BaseRepository
from app.models.user import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "test_token"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__('Users')

    def create_user(self, user: User) -> Any:
        query = sql.SQL("""
            INSERT INTO Users (name, email, password, client_number, customer_number)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, email, password, client_number, customer_number;
        """).format(table_name=sql.Identifier(self.table_name))

        values = (user.name, user.email, user.password, user.client_number, user.customer_number)

        user_data_tuple = self.execute_query(query, values)
        user_instance = User(**dict(zip(User.__annotations__, user_data_tuple)))
        return user_instance


    def get_users(self) -> Any:
        query = sql.SQL("""
            SELECT * FROM Users;
        """).format(table_name=sql.Identifier(self.table_name))

        user_data_list = self.execute_query_all(query)
        user_dict = [User(**dict(zip(User.__annotations__, user_data))) for user_data in user_data_list]
        return user_dict

    def get_user(self, user_id: int) -> Any:
        query = sql.SQL("""
            SELECT * FROM Users WHERE id = %s;
        """).format(table_name=sql.Identifier(self.table_name))

        values = (user_id,)

        user_data_tuple =  self.execute_query(query, values)
        user_instance = User(**dict(zip(User.__annotations__, user_data_tuple)))
        return user_instance

    def update_user(self, user_id: int, user: User) -> Any:
        query = sql.SQL("""
            UPDATE Users
            SET name = %s, email = %s, password = %s, client_number = %s, customer_number = %s
            WHERE id = %s
            RETURNING id, name, email, password, client_number, customer_number;
        """).format(table_name=sql.Identifier(self.table_name))

        values = (user.name, user.email, user.password, user.client_number, user.customer_number, user_id)

        user_data_tuple =  self.execute_query(query, values)
        user_instance = User(**dict(zip(User.__annotations__, user_data_tuple)))
        return user_instance

    def delete_user(self, user_id: int) -> Any:
        query = sql.SQL("""
            DELETE FROM Users WHERE id = %s
            RETURNING id, name, email, password, client_number, customer_number;
        """).format(table_name=sql.Identifier(self.table_name))

        values = (user_id,)

        user_data_tuple = self.execute_query(query, values)
        user_instance = User(**dict(zip(User.__annotations__, user_data_tuple)))
        return user_instance
