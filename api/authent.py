from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    db_manager,
    get_current_user
)
from .schemas import Token, deleteUserRequest

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

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    request: deleteUserRequest,
    current_user: str = Depends(get_current_user)
):
    try:
        if isinstance(current_user, str):
            current_username = current_user
        elif isinstance(current_user, dict):
            current_username = current_user.get("sub") or current_user.get("username")
        elif hasattr(current_user, "username"):
            current_username = current_user.username
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат данных пользователя",
            )

        if not current_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось определить имя пользователя",
            )
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash FROM Accounts WHERE username = ?",
                (current_username,),
            )
            user_row = cursor.fetchone()

            if not user_row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден",
                )
            if not verify_password(request.password, user_row[0]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Неверный пароль",
                )
            cursor.execute(
                "DELETE FROM Accounts WHERE username = ?",
                (current_username,),
            )
            
            conn.commit()

            return None

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка при удалении: {exc}")

