import httpx
import asyncio
import logging
from typing import Optional, Dict, Any
from models import ChatMessage

# 로깅 설정
logger = logging.getLogger(__name__)

API_URL = "https://dev.wenivops.co.kr/services/openai-api"

async def ask_chatgpt_async(
    user_id: str, 
    prompt_content: str, 
    max_retries: int = 3,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    ChatGPT API를 호출하여 응답을 받아옵니다.
    
    Args:
        user_id: 사용자 ID
        prompt_content: 사용자 입력 내용
        max_retries: 최대 재시도 횟수
        temperature: 응답의 창의성 조절 (0.0-2.0)
        max_tokens: 최대 토큰 수 제한
    
    Returns:
        str: AI 응답 내용
    """
    # 입력 검증
    if not prompt_content.strip():
        return "입력 내용이 비어있습니다."
    
    if len(prompt_content) > 4000:  # 토큰 제한 고려
        return "입력 내용이 너무 깁니다. 더 짧게 입력해주세요."
    
    # 메시지 구성
    messages_for_openai_api = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Please respond in Korean."
        },
        {
            "role": "user",
            "content": prompt_content
        }
    ]
    
    # 페이로드 구성
    payload = {
        "messages": messages_for_openai_api,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "user": user_id  # 사용자 추적을 위한 ID
    }
    
    # None 값 제거
    payload = {k: v for k, v in payload.items() if v is not None}
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ChatBot/1.0"
    }
    
    # 타임아웃 설정 (연결: 10초, 읽기: 30초)
    timeout = httpx.Timeout(connect=10.0, read=30.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(max_retries):
            try:
                logger.info(f"ChatGPT API 호출 시도 {attempt + 1}/{max_retries} - User: {user_id}")
                
                response = await client.post(
                    API_URL, 
                    json=payload, 
                    headers=headers
                )
                
                logger.info(f"응답 상태 코드: {response.status_code}")
                
                # 성공적인 응답 처리
                if response.status_code == 200:
                    result = response.json()
                    content = extract_content_from_response(result)
                    if content:
                        logger.info(f"성공적으로 응답 받음 - User: {user_id}")
                        return content
                    else:
                        logger.warning(f"응답 형식 오류: {result}")
                        return "AI 응답을 처리하는 중 오류가 발생했습니다."
                
                # Rate Limit 처리
                elif response.status_code == 429:
                    wait_time = min(2 ** attempt, 30)  # 최대 30초 대기
                    logger.warning(f"Rate limit 도달. {wait_time}초 대기 후 재시도...")
                    await asyncio.sleep(wait_time)
                    continue
                
                # 서버 오류 (5xx) - 재시도 가능
                elif 500 <= response.status_code < 600:
                    if attempt < max_retries - 1:
                        wait_time = min(2 ** attempt, 10)
                        logger.warning(f"서버 오류 ({response.status_code}). {wait_time}초 대기 후 재시도...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        return "서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
                
                # 클라이언트 오류 (4xx) - 재시도하지 않음
                elif 400 <= response.status_code < 500:
                    logger.error(f"클라이언트 오류: {response.status_code} - {response.text}")
                    return "요청 처리 중 오류가 발생했습니다. 입력 내용을 확인해주세요."
                
                # 기타 오류
                else:
                    logger.error(f"예상치 못한 응답 코드: {response.status_code}")
                    return f"알 수 없는 오류가 발생했습니다. (코드: {response.status_code})"
                    
            except httpx.TimeoutException:
                logger.warning(f"타임아웃 발생 - 재시도 {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    return "응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
                await asyncio.sleep(2 ** attempt)
                
            except httpx.RequestError as exc:
                logger.error(f"네트워크 오류 - 재시도 {attempt + 1}/{max_retries}: {exc}")
                if attempt == max_retries - 1:
                    return "네트워크 연결에 문제가 발생했습니다. 인터넷 연결을 확인해주세요."
                await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"예상치 못한 오류 - 재시도 {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    return "시스템 오류가 발생했습니다. 관리자에게 문의해주세요."
                await asyncio.sleep(2 ** attempt)
    
    return "최대 재시도 횟수를 초과했습니다. 잠시 후 다시 시도해주세요."


def extract_content_from_response(result: Dict[str, Any]) -> Optional[str]:
    """
    API 응답에서 콘텐츠를 추출합니다.
    
    Args:
        result: API 응답 JSON
        
    Returns:
        str: 추출된 콘텐츠 또는 None
    """
    try:
        # OpenAI 표준 형식
        if "choices" in result and result["choices"]:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                return content.strip() if content else None
        
        # 직접 content 필드
        elif "content" in result:
            content = result["content"]
            return content.strip() if content else None
            
        # 기타 가능한 형식들
        elif "response" in result:
            content = result["response"]
            return content.strip() if content else None
            
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"응답 파싱 오류: {e}")
        
    return None


# 사용 예시 및 테스트 함수
async def test_api():
    """API 테스트 함수"""
    response = await ask_chatgpt_async(
        user_id="test_user",
        prompt_content="안녕하세요! 간단한 인사말을 해주세요.",
        max_retries=2
    )
    print(f"응답: {response}")


if __name__ == "__main__":
    asyncio.run(test_api())