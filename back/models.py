from pydantic import BaseModel, Field
from typing import Optional, Literal
import uuid

# --- 사용자
class UserCreate(BaseModel): # 회원가입
    username: str
    email: str
    password: str
    nickname: Optional[str] = None

class UserLogin(BaseModel): # 로그인할 때 받을 정보
    username: str
    password: str

class User(BaseModel): # 실제로 저장할 사용자 정보
    id: int 
    username: str
    email: str
    nickname: str
    hashed_password: str # 암호화된 비밀번호

class UserResponse(BaseModel): # 다른 사람에게 보여줄 사용자 정보(비밀번호 제외)
    id: int # 사용자 고유번호
    username: str
    email: str
    nickname: str




# --- 채팅
class ChatMessage(BaseModel):
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    senderType: Literal["user", "ai"]
    content: str
    # timestamp: datetime


class ChatRequest(BaseModel): # 채팅 요청
    userId: Optional[str] = None
    content: str