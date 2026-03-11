from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    db_manager,
)
from .schemas import Token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return a JWT access token."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, password_hash FROM Accounts WHERE username = ?",
                (credentials.username,),
            )
            user_row = cursor.fetchone()

            if not user_row or not verify_password(
                credentials.password, user_row[1]
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверное имя пользователя или пароль",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = create_access_token(
                data={"sub": user_row[0]}, expires_delta=expires
            )
            return Token(access_token=token, token_type="bearer")

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {exc}")
