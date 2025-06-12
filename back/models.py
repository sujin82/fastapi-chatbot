from pydantic import BaseModel, Field
from typing import Optional, Literal
import uuid

# --- Pydantic 스키마 정의 ---
class User(BaseModel):
    """ 사용자 기본 정보 스키마 """
    userId: str
    userPwd: str
    nickname: Optional[str] = None

class ChatMessage(BaseModel):
    """ 개별 대화 메시지를 나타내는 스키마.
    각 메시지에 사용자 ID를 직접 연결 """
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    senderType: Literal["user", "ai"]
    content: str
    # timestamp: datetime

class ChatRequest(BaseModel):
    """ 채팅 요청 스키마 """
    userId: Optional[str] = None
    content: str

class LoginRequest(BaseModel):
    userId: str
    userPwd: str

class LoginResponse(BaseModel):
    userId: str
    message: str