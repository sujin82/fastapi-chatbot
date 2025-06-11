from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
# from typing import List, Optional
# import openai

app = FastAPI()

# CORS 설정 (프론트엔드와 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


users = [] # 사용자 목록
conversations = [] # 대화 기록
scenarios = [] # 생성된 시나리오

# Pydantic 스키마 정의
class User(BaseModel):
    """사용자 기본 정보 스키마"""
    userId: str
    userPwd: str
    nickname: Optional[str]

# 앤드포인트 설계



