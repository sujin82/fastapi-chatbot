from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from auth import users_db, user_sessions # auth.py에서 users_db, user_sessions 임포트
from models import UserCreate, UserLogin, User, UserResponse, ChatMessage, ChatRequest
from chatgpt_api import ask_chatgpt_async # chatgpt_api.py에서 ask_chatgpt_async 함수 임포트

app = FastAPI()

# --- CORS 설정 (프론트엔드와 통신을 위해) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 메모리 내 데이터베이스 (실제 데이터베이스 대신 사용) ---
messages_db: Dict[str, ChatMessage] = {}


@app.post("/register/", summary="회원가입")
async def register_user(user: UserCreate):
    """
    새로운 **사용자**를 시스템에 등록합니다.
    `userId`가 이미 존재하면 오류를 반환합니다.
    """
    if user.userId in users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자 ID 입니다")
    users_db[user.userId] = user
    print(f"새 사용자 등록: {user.userId}")
    return user

@app.post("/login/", response_model=UserResponse, summary="사용자 로그인")
async def login(request: UserLogin):
    """
    사용자 로그인 처리를 합니다.
    """
    user_id = request.userId
    user_pwd = request.userPwd
    
    user = users_db.get(user_id)
    if not user:  # 아이디 검증
        raise HTTPException(status_code=401, detail="사용자 ID를 찾을 수 없습니다.")
        
    if user.userPwd != user_pwd:  # 비밀번호 검증
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
        
    user_sessions.add(user_id) # 로그인 세션에 사용자 ID 추가
    
    return UserResponse(message="로그인 성공", userId=user_id)

@app.post("/chat/", response_model=ChatMessage)
async def send_message(request: ChatRequest):
    """
    AI에게 메시지를 보내고 응답을 받습니다.
    """
    user_id = request.userId or "guest"
    user_message_content = request.content

    # 사용자 메시지 생성 및 DB 저장
    user_message = ChatMessage(
        userId=user_id,
        senderType="user",
        content=user_message_content
    )
    messages_db[user_message.messageId] = user_message

    # ask_chatgpt_async 함수 호출
    try:
        # chatgpt_api.py에서 ask_chatgpt_async 함수가 이제 오류 시에도 문자열을 반환하도록
        # 수정되었으므로, 여기서 발생하는 ResponseValidationError는 해결될 것입니다.
        bot_response_content = await ask_chatgpt_async(user_id=user_id, prompt_content=user_message_content)
    except Exception as e:
        # ask_chatgpt_async 함수 내에서 모든 오류를 문자열로 처리하도록 했지만,
        # 혹시 모를 다른 종류의 예외에 대비하여 try-except를 유지합니다.
        raise HTTPException(status_code=500, detail=f"챗봇 서버에서 오류가 발생했습니다: {str(e)}")

    # 챗봇 응답을 ChatMessage 객체로 생성하고 DB에 저장
    bot_message = ChatMessage(
        userId=user_id,
        senderType="ai", # AI의 메시지임을 나타냅니다.
        content=bot_response_content
    )
    messages_db[bot_message.messageId] = bot_message
    return bot_message