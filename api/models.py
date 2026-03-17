from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, Text, Boolean,DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

Base = declarative_base()

class Account(Base):
    __tablename__ = 'Accounts'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(260), nullable=False)
    first_name = Column(String(80), nullable=False)
    surname = Column(String(80), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
         return f"<Account id={self.id} username='{self.username}'>"

class Chats(Base):
    __tablename__ = 'Chats'

    ChatID = Column(Integer, primary_key=True, autoincrement=True)
    ChatName = Column(String(100), nullable=False)
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    user1_id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)

    def __repr__(self):
        return f"<Chats ChatID={self.ChatID} ChatName='{self.ChatName}'>"

class Messages(Base):
    __tablename__ = 'Messages'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Добавлю id, если нужно, но по таблице не указано, но для SQLAlchemy нужен primary key
    chat_Id = Column(Integer, ForeignKey('Chats.ChatID'), nullable=False)
    user_Id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)
    MessagesText = Column(Text, nullable=False)
    sentAt = Column(DateTime, server_default=func.now())
    isRead = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Messages id={self.id} chat_Id={self.chat_Id} user_Id={self.user_Id} MessagesText='{self.MessagesText[:20]}...'>"
    
class currencyItem(BaseModel):
    id: Optional[int] = None
    quantity: int
    get_Time: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)