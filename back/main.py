from fastapi import FastAPI, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Optional

from models import UserCreate, UserLogin, User, UserResponse, ChatMessage, ChatRequest
from auth import create_user, authenticate_user, create_session, get_current_user, logout_user

from chatgpt_api import ask_chatgpt_async

app = FastAPI()
app.mount("/static", StaticFiles(directory="../front"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages_db: Dict[str, ChatMessage] = {}

# @app.get("/")
# async def read_root():
#     return {"message": "Hello, FastAPI! This is a minimal test."}

@app.get("/")
async def read_index():
    return FileResponse("../front/index.html")

@app.get("/login")
async def read_login():
    return FileResponse("../front/login.html")

@app.get("/register")
async def read_register():
    return FileResponse("../front/register.html")


@app.post("/register", summary="회원가입")
async def register_user(user_data: UserCreate):
    result = create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    if not result["success"]:
        # 실패했을 때 (예: 이미 존재하는 사용자명)
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )
    
    user_response = UserResponse(
        id=result["user"].id,
        username=result["user"].username,
        email=result["user"].email
        # 비밀번호는 절대 포함하지 않음!
    )

    return {
        "message": "🎉 회원가입이 완료되었습니다!",
        "user": user_response
    }


@app.post("/login", summary="사용자 로그인")
async def login(user_data: UserLogin):
    user = authenticate_user(user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="❌ 사용자명 또는 비밀번호가 올바르지 않습니다"
        )

    session_id = create_session(user_data.username)

    response = JSONResponse({
        "message": "🎉 로그인 성공!",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })

    response.set_cookie(
        key="session_id",           # 쿠키 이름
        value=session_id,           # 세션 ID
        httponly=True,              # 보안: JavaScript로 접근 불가
        max_age=3600                # 1시간 후 만료
    )

    return response


@app.get("/me")
async def 내정보보기(session_id: Optional[str] = Cookie(None)):
    """
    👤 현재 로그인한 사용자 정보 보기

    과정:
    1. 브라우저에서 "입장권" 확인
    2. "입장권"이 유효한지 검사
    3. 유효하면 사용자 정보 반환
    """

    # 1️⃣ 입장권(세션 ID) 확인
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="🚫 로그인이 필요합니다"
        )

    # 2️⃣ 입장권이 유효한지 확인
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="🚫 유효하지 않은 세션입니다. 다시 로그인해주세요"
        )

    # 3️⃣ 사용자 정보 반환 (비밀번호 제외)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email
    )


@app.post("/logout")
async def 로그아웃(session_id: Optional[str] = Cookie(None)):
    """
    🚪 로그아웃 처리

    과정:
    1. "입장권" 회수 (세션 삭제)
    2. 브라우저에서도 "입장권" 삭제
    """

    # 1️⃣ 세션 삭제 (있다면)
    if session_id:
        logout_user(session_id)

    # 2️⃣ 응답 만들기
    response = JSONResponse({"message": "👋 로그아웃되었습니다"})

    # 3️⃣ 브라우저에서 쿠키 삭제
    response.delete_cookie("session_id")

    return response




@app.post("/chat", response_model=ChatMessage)
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