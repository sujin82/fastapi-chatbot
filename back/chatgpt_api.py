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
    

    payload_to_send = formatted_messages

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(API_URL, json=payload_to_send, headers=headers)
                print("🔄 응답 상태 코드:", response.status_code)
                print("📦 응답 본문:", response.text)

                if response.status_code == 200:
                    result = response.json()
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