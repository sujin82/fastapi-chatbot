import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://dev.wenivops.co.kr/services/openai-api"
API_KEY = os.getenv("OPENAI_API_KEY")

def ask_chatgpt(prompt: str) -> str:
    try:
        # messages 배열만 전송 (model, max_tokens 제거)
        payload = [
            {"role": "system", "content": "assistant는 시인이다."},
            {"role": "user", "content": prompt}
        ]
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        print("보내는 payload:", payload)
        response = requests.post(API_URL, json=payload, headers=headers)
        print("응답코드:", response.status_code)
        print("응답본문:", response.text)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        print("ask_chatgpt 에러:", e)
        raise