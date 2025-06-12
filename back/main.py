from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict
import os

from auth import users_db, user_sessions
from models import UserCreate, UserLogin, User, UserResponse, ChatMessage, ChatRequest
from chatgpt_api import ask_chatgpt_async

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages_db: Dict[str, ChatMessage] = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'front')


@app.post("/register/", summary="회원가입")
async def register_user(user: UserCreate):
    if user.userId in users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 ID 입니다")
    users_db[user.userId] = user
    print(f"새 사용자 등록: {user.userId}")
    return user

@app.post("/login/", response_model=UserResponse, summary="사용자 로그인")
async def login(request: UserLogin):
    user_id = request.userId
    user_pwd = request.userPwd
    
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="사용자 ID를 찾을 수 없습니다.")
        
    if user.userPwd != user_pwd:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
        
    user_sessions.add(user_id)
    
    return UserResponse(message="로그인 성공", userId=user_id)

@app.post("/chat/", response_model=ChatMessage)
async def send_message(request: ChatRequest):
    user_id = request.userId or "guest"
    user_message_content = request.content

    user_message = ChatMessage(
        userId=user_id,
        senderType="user",
        content=user_message_content
    )
    messages_db[user_message.messageId] = user_message

    try:
        bot_response_content = await ask_chatgpt_async(user_id=user_id, prompt_content=user_message_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 서버에서 오류가 발생했습니다: {str(e)}")

    bot_message = ChatMessage(
        userId=user_id,
        senderType="ai",
        content=bot_response_content
    )
    messages_db[bot_message.messageId] = bot_message
    return bot_message

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static_files")