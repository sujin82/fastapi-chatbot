import hashlib
import uuid
from typing import Optional
from models import User


users_db = {  # 사용자 정보 저장소
    "user1": User(  # ⭐ User 모델의 인스턴스를 생성하여 저장합니다.
        id=1,
        username="user1",
        email="user1@example.com",
        hashed_password=hashlib.sha256("pass1111".encode()).hexdigest()
    ),
    "user2": User(  # ⭐ User 모델의 인스턴스를 생성하여 저장합니다.
        id=2,
        username="user2",
        email="user2@example.com",
        hashed_password=hashlib.sha256("pass2222".encode()).hexdigest()
    )
}
user_sessions = {}      # 로그인 세션 저장소
next_user_id = 3        # 다음에 만들 사용자의 ID 번호

def hash_password(password: str) -> str:
    """
    🔒 비밀번호를 암호화하는 함수

    예시:
    입력: "my_password123"
    출력: "ef92b778bafe771e89245b89ecbc08a44724137abefb4ad56..."
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(입력한_비밀번호: str, 저장된_암호화_비밀번호: str) -> bool:
    """
    🔍 비밀번호가 맞는지 확인하는 함수

    과정:
    1. 입력한 비밀번호를 암호화
    2. 저장된 암호화 비밀번호와 비교
    3. 같으면 True, 다르면 False
    """
    입력한_비밀번호_암호화 = hash_password(입력한_비밀번호)
    return 입력한_비밀번호_암호화 == 저장된_암호화_비밀번호

def create_user(username: str, email: str, password: str) -> dict:
    """
    👤 새로운 사용자를 만드는 함수
    """
    global next_user_id

    # 1️⃣ 이미 같은 이름의 사용자가 있는지 확인
    if username in users_db:
        return {
            "success": False,
            "message": "이미 존재하는 사용자명입니다"
        }

    # 2️⃣ 새로운 사용자 정보 만들기
    from models import User
    new_user = User(
        id=next_user_id,                          # 고유 번호
        username=username,                        # 사용자명
        email=email,                             # 이메일
        hashed_password=hash_password(password)   # 암호화된 비밀번호
    )

    # 3️⃣ 데이터베이스에 저장
    users_db[username] = new_user
    next_user_id += 1  # 다음 사용자를 위해 번호 증가

    return {"success": True, "user": new_user}

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    🔑 로그인 시도하는 함수

    과정:
    1. 사용자명이 존재하는지 확인
    2. 비밀번호가 맞는지 확인
    3. 둘 다 맞으면 사용자 정보 반환
    """
    # 1️⃣ 사용자명 확인
    if username not in users_db:
        return None  # 사용자가 없음

    # 2️⃣ 저장된 사용자 정보 가져오기
    user = users_db[username]

    # 3️⃣ 비밀번호 확인
    if not verify_password(password, user.hashed_password):
        return None  # 비밀번호가 틀림

    # 4️⃣ 모든 검증 통과!
    return user

def create_session(username: str) -> str:
    """
    🎫 로그인 성공 후 "입장권" 만들어주는 함수

    마치 영화관 티켓처럼:
    - 고유한 번호가 적힌 티켓 발급
    - 나중에 이 티켓으로 신분 확인
    """
    session_id = str(uuid.uuid4())  # 완전히 랜덤한 ID 생성
    user_sessions[session_id] = username  # 세션과 사용자 연결
    return session_id

def get_current_user(session_id: str) -> Optional[dict]:
    """
    🎫 "입장권"을 보고 누구인지 확인하는 함수

    과정:
    1. 세션 ID가 유효한지 확인
    2. 해당 세션의 사용자명 찾기
    3. 사용자 정보 반환
    """
    # 1️⃣ 세션 ID 확인
    if session_id not in user_sessions:
        return None  # 유효하지 않은 세션

    # 2️⃣ 사용자명 찾기
    username = user_sessions[session_id]

    # 3️⃣ 사용자 정보 반환
    return users_db.get(username)

def logout_user(session_id: str):
    """
    🚪 로그아웃하는 함수 (입장권 회수)
    """
    if session_id in user_sessions:
        del user_sessions[session_id]  # 세션 삭제