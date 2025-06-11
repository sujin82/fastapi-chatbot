from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
import uuid
import asyncio

from chatgpt_api import ask_chatgpt_async  # 비동기 버전 임포트

app = FastAPI()

# --- CORS 설정 (프론트엔드와 통신을 위해) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# --- 메모리 내 데이터베이스 (실제 데이터베이스 대신 사용) ---
users_db: Dict[str, User] = {}
messages_db: Dict[str, ChatMessage] = {} # {message_id: ChatMessage 객체} 형태로 저장
logged_in_users: set[str] = set()  # 현재 로그인된 사용자 ID를 저장하는 간단한 세션 저장소

# --- 엔드포인트 설계 ---
@app.post("/register/", response_model=User, summary="회원가입")
async def register_user(user: User):
    """
    새로운 **사용자**를 시스템에 등록합니다.
    `userId`가 이미 존재하면 오류를 반환합니다.
    """
    if user.userId in users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 ID 입니다")
    users_db[user.userId] = user
    print(f"새 사용자 등록: {user.userId}")
    return user

@app.post("/login/", response_model=LoginResponse, summary="사용자 로그인")
async def login(request: LoginRequest):
    user_id = request.userId
    user_pwd = request.userPwd
    
    user = users_db.get(user_id)
    if not user:  # 아이디 검증
        raise HTTPException(status_code=401, detail="사용자 ID를 찾을 수 없습니다.")
        
    if user.userPwd != user_pwd:  # 비밀번호 검증
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
        
    logged_in_users.add(user_id)
    
    return LoginResponse(message="로그인 성공", userId=user_id)

@app.post("/chat/", response_model=ChatMessage)
async def send_message(request: ChatRequest):
    user_id = request.userId or "guest"
    user_message = ChatMessage(
        userId=user_id,
        senderType="user",
        content=request.content
    )
    messages_db[user_message.messageId] = user_message

    # --- 여기서부터 변경 ---
    # ask_chatgpt_async 함수가 ChatMessage 객체 리스트를 기대하므로,
    # ChatMessage 객체로 구성된 chat_history_for_api를 만듭니다.
    
    chat_history_for_api: List[ChatMessage] = []

    # 1. 시스템 메시지 추가 (ChatMessage 객체로 생성)
    # 시스템 메시지는 실제 사용자가 보낸 것은 아니지만, 대화의 맥락을 제공합니다.
    system_intro_message = ChatMessage(
        messageId=str(uuid.uuid4()), # 시스템 메시지용 고유 ID 생성
        userId="system",             # 시스템 메시지를 위한 userId
        senderType="ai",             # 시스템 메시지는 AI 역할로 간주
        content="You are a helpful assistant."
    )
    chat_history_for_api.append(system_intro_message)

    # 2. 현재 사용자 메시지 추가
    chat_history_for_api.append(user_message)

    # 3. (선택 사항: 이전 대화 기록 추가)
    # 실제 챗봇에서는 `messages_db`에서 이전 대화 기록을 가져와 여기에 추가하여
    # 챗봇이 대화의 맥락을 기억하도록 할 수 있습니다.
    # 예:
    # sorted_past_messages = sorted(messages_db.values(), key=lambda msg: msg.timestamp) # timestamp 필드가 ChatMessage에 추가되어야 함
    # for msg in sorted_past_messages:
    #     if msg.userId == user_id: # 특정 사용자의 이전 메시지만 포함
    #         chat_history_for_api.append(msg)
    # 현재 `messages_db`는 전체 메시지를 담고 있으므로, 필요에 따라 필터링 및 정렬 로직 추가 필요

    try:
        # ChatMessage 객체 리스트를 ask_chatgpt_async 함수에 전달
        bot_response = await ask_chatgpt_async(chat_history_for_api)
    except Exception as e:
        # 챗봇 API 호출 중 오류 발생 시 500 에러 반환
        raise HTTPException(status_code=500, detail=f"챗봇 서버에서 오류가 발생했습니다: {str(e)}")

    # 챗봇 응답을 ChatMessage 객체로 생성하고 DB에 저장
    bot_message = ChatMessage(
        userId=user_id,
        senderType="ai",
        content=bot_response
    )
    messages_db[bot_message.messageId] = bot_message
    return bot_message