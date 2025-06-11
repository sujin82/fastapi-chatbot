from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from datetime import datetime
import uuid

app = FastAPI()

# --- CORS 설정 (프론트엔드와 통신을 위해) --- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# --- Pydantic 스키마 정의 --- #
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

class LoginRequest(BaseModel):
    userId: str
    userPwd: str

class LoginResponse(BaseModel):
    userId: str
    message: str



# --- 메모리 내 데이터베이스 (실제 데이터베이스 대신 사용) --- #
users_db: dict[str, User] = {}
messages_db: dict[str, ChatMessage] = {}
logged_in_users: set[str] = set() # 현재 로그인된 사용자 ID를 저장하는 간단한 세션 저장소



# --- 앤드포인트 설계 --- #
@app.post("/register/", response_model=User, summary="회원가입")
def register_user(user: User):
    """
    새로운 **사용자**를 시스템에 등록합니다.
    `userId`가 이미 존재하면 오류를 반환합니다.
    """
    if user.userId in users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 ID 입니다")
    users_db[user.userId] = user
    print(User)
    return user


@app.post("/login/", response_model=LoginResponse, summary="사용자 로그인")
def login(request: LoginRequest):
    user_id = request.userId
    user_pwd = request.userPwd

    user = users_db.get(user_id)
    if not user: # 아이디 검증
        raise HTTPException(status_code=401, detail="사용자 ID를 찾을 수 없습니다.")
    
    if user.userPwd != user_pwd:    # 비밀번호 검증
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    
    logged_in_users.add(user_id)

    return LoginResponse(message="로그인 성공", userId=user_id)


@app.post("/chat/", response_model=ChatMessage, summary="사용자 메시지 전송 및 챗봇 응답")
def send_message(request: ChatMessage):
    """
    사용자가 **메시지**를 전송하고, 챗봇이 가상의 응답을 생성합니다.
    - `userId`: 메시지를 보내는 사용자 ID (필수)
    - `content`: 사용자의 메시지 내용 (필수)

    **응답:** 서버에 저장된 사용자 메시지가 반환됩니다. 챗봇 응답은 내부적으로 처리됩니다.
    """
    if request.userId not in users_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자 ID입니다. 메시지를 보내기 전에 사용자를 등록해주세요.")

    # 2. 사용자 메시지 생성 및 저장 (messageId, timestamp 자동 생성)
    user_message = ChatMessage(
        userId=request.userId,
        senderType="user",
        content=request.content
    )
    messages_db[user_message.messageId] = user_message
    print(f"사용자 ({user_message.userId}): {user_message.content}")

    # 4. 챗봇 메시지 생성 및 저장 (messageId, timestamp 자동 생성)
    bot_message = ChatMessage(
        userId=request.userId,
        senderType="ai",
        content="안녕하세요! 무엇을 도와드릴까요?"
    )
    messages_db[bot_message.messageId] = bot_message
    print(f"챗봇 ({bot_message.userId}): {bot_message.content}")

    # 5. 사용자 메시지 반환
    return user_message

# /chat/{user_id} : 대화 기록 조회용(시간되면 추가) +++++++++++++++++++++