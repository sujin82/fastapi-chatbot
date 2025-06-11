import httpx
from typing import Optional, Literal, List
import asyncio
import json
import uuid
from pydantic import BaseModel, Field

# ChatMessage 스키마는 main.py와 동일하게 유지
class ChatMessage(BaseModel):
    """ 개별 대화 메시지를 나타내는 스키마.
    각 메시지에 사용자 ID를 직접 연결 """
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    senderType: Literal["user", "ai"]
    content: str
    # timestamp: datetime # timestamp는 현재 코드에서 사용되지 않으므로 주석 처리하거나 필요시 사용

API_URL = "https://dev.wenivops.co.kr/services/openai-api"

async def ask_chatgpt_async(messages: List[ChatMessage], max_retries: int = 3) -> str:
    if not messages or not isinstance(messages, list):
        raise Exception("messages는 비어있거나 올바르지 않은 형식입니다.")
    
    # ChatMessage 객체를 OpenAI API가 요구하는 형식의 딕셔너리 리스트로 변환
    formatted_messages = []
    for msg in messages:
        role_mapping = {
            "user": "user",
            "ai": "assistant"
        }
        formatted_messages.append({
            "role": role_mapping.get(msg.senderType, "user"),
            "content": msg.content
        })
    
    # --- 변경된 부분 시작 ---
    # 프록시 서버가 'messages' 배열 자체를 최상위 페이로드로 기대하는 경우를 시도합니다.
    # 이전에는 {"model": "...", "messages": [...]} 형태였으나,
    # 프록시 서버의 오류 메시지가 'messages' 필드의 타입 문제임을 명확히 지적하므로
    # 'formatted_messages' (리스트) 그 자체를 페이로드로 보냅니다.
    # 'model' 정보가 필요하다면, 해당 프록시 API의 문서를 확인하여
    # 'model'을 쿼리 파라미터나 다른 방식으로 전달해야 할 수 있습니다.
    payload_to_send = formatted_messages
    # --- 변경된 부분 끝 ---

    headers = {
        "Content-Type": "application/json"
    }

    print("🚀 보낼 payload:", json.dumps(payload_to_send, indent=2, ensure_ascii=False))

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(API_URL, json=payload_to_send, headers=headers)
                print("🔄 응답 상태 코드:", response.status_code)
                print("📦 응답 본문:", response.text)

                if response.status_code == 200:
                    result = response.json()
                    # 이 오류는 이제 발생하지 않아야 합니다. (프록시가 유효한 응답을 보내면)
                    if "choices" not in result:
                        raise Exception(f"API 응답에 choices가 없습니다: {result}")
                    
                    return result["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    print(f"재시도 {attempt + 1}/{max_retries}: 429 Rate Limit. 대기 중...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    raise Exception(f"API 오류: {response.status_code} - {response.text}")
            except httpx.RequestError as exc:
                print(f"재시도 {attempt + 1}/{max_retries}: 요청 중 오류 발생 - {exc}. 대기 중...")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                print(f"재시도 {attempt + 1}/{max_retries}: 예상치 못한 오류 발생 - {e}. 대기 중...")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

# 사용 예시 (테스트용 - 실제 작동은 main.py를 통해 이루어집니다)
async def main():
    try:
        messages_to_send = [
            ChatMessage(userId="user123", senderType="user", content="지구는 왜 파란가요?")
        ]
        
        response_content = await ask_chatgpt_async(messages_to_send)
        print("\n✨ 최종 응답:", response_content)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())
