from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from api.database import get_db
from api.models import Chats, Messages
from api.schemas import ChatsCreate, ChatsResponse, MessagesCreate, MessagesResponse
from api.security import get_current_user
from api.models import Account
import traceback
from api.security import get_current_user

router = APIRouter(tags=["Chats"], prefix="/Chatiks")

@router.post("/chats/", response_model=ChatsResponse)
def create_chat(chat: ChatsCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        current_user_id = current_user["id"]
        if current_user_id == chat.user2_id:
            raise HTTPException(status_code=400, detail="Нельзя создать чат с самим собой")
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Пользователь не авторизован")
        interlocutor = db.query(Account).filter(Account.id == chat.user2_id).first()
        if not interlocutor:
            raise HTTPException(status_code=404, detail="Пользователь для чата не найден")
        current_User = db.query(Account).filter(Account.id == current_user_id).first()
        user2 = db.query(Account).filter(Account.id == chat.user2_id).first()
        if not current_User or not user2:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        db_chat = Chats(ChatName=chat.ChatName
                        , user1_id=current_user_id
                        , user2_id=chat.user2_id
                    )
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания чата: {str(e)}")
    

@router.get("/chats/", response_model=list[ChatsResponse])
def read_chats(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")
    chats = db.query(Chats).filter(
        or_(
            Chats.user1_id == user_id,
            Chats.user2_id == user_id
        )
    ).order_by(Chats.CreatedAt.desc()).offset(skip).limit(limit).all()
    
    return chats

@router.post("/messages/", response_model=MessagesResponse)
def create_message(message: MessagesCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    chat = db.query(Chats).filter(Chats.ChatID == message.chat_Id).first()
    user_id = current_user["id"]
    try:
     if not current_user or "id" not in current_user:
            raise HTTPException(status_code=401, detail="Пользователь не авторизован")
     if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
     if user_id not in [chat.user1_id, chat.user2_id]:
        raise HTTPException(status_code=403, detail="Нет доступа к этому чату")
     
     db_message = Messages(
            chat_Id=message.chat_Id,
            user_Id= user_id,
            MessagesText=message.MessagesText)
     db.add(db_message)
     db.commit()
     db.refresh(db_message)
     if db_message is None:
            raise Exception("Не удалось сохранить сообщение")
     return db_message
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.get("/messages/{chat_id}", response_model=list[MessagesResponse])
def read_messages(chat_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    if not user_id:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")
    chat = db.query(Chats).filter(Chats.ChatID == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    
    if current_user["id"] not in [chat.user1_id, chat.user2_id]:
        raise HTTPException(status_code=403, detail="Нет доступа к этому чату")

    messages = db.query(Messages).filter(Messages.chat_Id == chat_id).order_by(Messages.sentAt.asc()).offset(skip).limit(limit).all()
    return messages