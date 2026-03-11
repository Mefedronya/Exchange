from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import os
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import pyodbc


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "9c0ff8c9299ea0832b4b0c6361a4324ac84159806dcc9700decad80de6f219c9")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password, hashed_password):
    #проверка пароля на соответствие хэшу
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password: str):
    #хэширование пароля
    return pwd_context.hash(password)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class databaseManager:
    def __init__(self):
        self.server = 'DESKTOP-P5B9MPU\\SQLEXPRESS'
        self.database = 'it_planet'
        self.connection_string = (f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                                  f"SERVER={self.server};"
                                  f"DATABASE={self.database};"
                                  "Trusted_Connection=yes;")
        
    def get_connection(self):
        return pyodbc.connect(self.connection_string) 

db_manager = databaseManager()
# Проверка подключения при старте (опционально)
try:
    db_manager.get_connection().close()
except Exception as e:
    print(f"Warning: Could not connect to DB at startup: {e}")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")  
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    try:        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, first_name, surname, created_at FROM Accounts WHERE username = ?",
                (token_data.username,)
            )
            user_row = cursor.fetchone()
            
            if user_row is None:
                raise credentials_exception
            
            return {
                "id": user_row[0],
                "username": user_row[1],
                "first_name": user_row[2],
                "surname": user_row[3],
                "created_at": user_row[4]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")