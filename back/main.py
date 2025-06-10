from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 (프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "방구석 힐링 챗봇 서버가 실행 중입니다!"}


#  API 엔드포인트 설계
# 사용자 관련
# POST /register    # 회원가입
# POST /login       # 로그인

# # 채팅 관련  
# POST /chat        # AI와 대화
# GET /history      # 대화 기록 조회

# # 기타
# GET /             # 서버 상태 확인


# 데이터베이스 스키마(딕셔너리 버전)
# 사용자 정보
# users = {
#     "username": {
#         "password": "비밀번호",
#         "conversations": [
#             {
#                 "question": "미래에 뭐하고 싶어?",
#                 "answer": "AI가 답변한 내용...",
#                 "timestamp": "2025-06-10 14:30"
#             }
#         ]
#     }
# }

# # 현재 로그인 세션
# sessions = {"session_id": "username"}