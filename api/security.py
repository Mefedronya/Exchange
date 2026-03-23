from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import os
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import pyodbc
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "9c0ff8c9299ea0832b4b0c6361a4324ac84159806dcc9700decad80de6f219c9")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ✅ ИСПРАВЛЕННЫЙ КЛАСС ПОДКЛЮЧЕНИЯ
class DatabaseManager:
    def __init__(self):
        # Берем настройки из переменных окружения (как в run.py)
        self.server = os.getenv("DB_SERVER", "localhost")
        self.port = os.getenv("DB_PORT", "1433")
        self.database = os.getenv("DB_NAME", "it_planet")
        self.username = os.getenv("DB_USER", "sa")
        self.password = os.getenv("DB_PASSWORD", "")
        self.driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        self.trust_cert = os.getenv("DB_TRUST_CERT", "yes").lower() == "yes"
        
        # ✅ Единая строка подключения с TrustServerCertificate
        self.connection_string = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"TrustServerCertificate={'yes' if self.trust_cert else 'no'};"
            f"Connection Timeout=30;"
        )
        
    def get_connection(self):
        return pyodbc.connect(self.connection_string)

db_manager = DatabaseManager()

# Проверка подключения при старте
try:
    conn = db_manager.get_connection()
    conn.close()
    print("✅ Security module: Database connection verified!")
except Exception as e:
    print(f"❌ Security module: Database connection failed: {e}")
    # Не прерываем запуск, но логируем ошибку

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
        print(f"❌ Database error in get_current_user: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
