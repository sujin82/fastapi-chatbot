import httpx
import asyncio
from models import ChatMessage

API_URL = "https://dev.wenivops.co.kr/services/openai-api"

async def ask_chatgpt_async(user_id: str, prompt_content: str, max_retries: int = 3) -> str:
    messages_for_openai_api = []

    system_intro_message = {
        "role": "system",
        "content": "You are a helpful assistant."
    }
    messages_for_openai_api.append(system_intro_message)

    user_message_for_openai = {
        "role": "user",
        "content": prompt_content
    }
    messages_for_openai_api.append(user_message_for_openai)

    payload_to_send_to_proxy = messages_for_openai_api

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(API_URL, json=payload_to_send_to_proxy, headers=headers)
                print("🔄 응답 상태 코드:", response.status_code) #
                print("📦 응답 본문:", response.text) #

                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and result["choices"]:
                        return result["choices"][0]["message"]["content"]
                    elif "content" in result:
                        return result["content"]
                    else:
                        print(f"Proxy response missing expected content structure: {result}")
                        return "AI 응답 형식이 예상과 다릅니다. (프록시 서버 응답 확인 필요)"
                elif response.status_code == 429:
                    print(f"재시도 {attempt + 1}/{max_retries}: 429 Rate Limit. 잠시 대기 중...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    return f"API 오류가 발생했습니다: {response.status_code} - {response.text}"
            
            except httpx.RequestError as exc:
                print(f"재시도 {attempt + 1}/{max_retries}: 네트워크 요청 중 오류 발생 - {exc}. 잠시 대기 중...")
                if attempt == max_retries - 1:
                    return f"네트워크 요청 오류: {exc}"
                await asyncio.sleep(2 ** attempt)
            
            except Exception as e:
                print(f"재시도 {attempt + 1}/{max_retries}: 예상치 못한 오류 발생 - {e}. 잠시 대기 중...")
                if attempt == max_retries - 1:
                    return f"예상치 못한 오류: {e}"
                await asyncio.sleep(2 ** attempt)
        
        return "최대 재시도 횟수를 초과했거나 알 수 없는 오류가 발생했습니다."