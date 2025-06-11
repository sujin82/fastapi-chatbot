import requests
import time
import json

API_URL = "https://dev.wenivops.co.kr/services/openai-api"

def ask_chatgpt(prompt: str, max_retries: int = 3) -> str:
    # 1. API 키 확인
    
    # 2. 입력 검증
    if not prompt.strip():
        raise Exception("질문 내용이 비어있거나 공백만 포함되어 있습니다.")
    
    if len(prompt) > 4000:
        raise Exception("질문이 너무 깁니다. 4000자 이내로 입력해주세요.")
    
    # 3. 페이로드 준비
    payload = [
        {"role": "system", "content": ""},
        {"role": "user", "content": prompt.strip()}
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_URL}"
    }
    
    # 4. 재시도 로직 (일시적 오류 대응)
    last_error = None
    
    for attempt in range(max_retries):
        try:
            print(f"API 호출 시도 {attempt + 1}/{max_retries}")
            print("보내는 payload:", payload)
            
            # 5. 타임아웃 설정 (30초)
            response = requests.post(
                API_URL, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            
            print("응답코드:", response.status_code)
            print("응답본문:", response.text)
            
            # 6. 응답 상태 코드별 처리
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # 응답 구조 검증
                    if "choices" not in result:
                        raise Exception("API 응답에 'choices' 필드가 없습니다.")
                    
                    if len(result["choices"]) == 0:
                        raise Exception("API 응답의 'choices' 배열이 비어있습니다.")
                    
                    if "message" not in result["choices"][0]:
                        raise Exception("API 응답에 'message' 필드가 없습니다.")
                    
                    if "content" not in result["choices"][0]["message"]:
                        raise Exception("API 응답에 'content' 필드가 없습니다.")
                    
                    content = result["choices"][0]["message"]["content"]
                    
                    if not content:
                        raise Exception("API 응답 내용이 비어있습니다.")
                    
                    return content
                    
                except json.JSONDecodeError:
                    raise Exception("API 응답을 JSON으로 파싱할 수 없습니다.")
            
            elif response.status_code == 400:
                raise Exception("잘못된 요청입니다. 입력 데이터를 확인해주세요.")
            
            elif response.status_code == 403:
                raise Exception("API 접근 권한이 없습니다.")
            
            elif response.status_code == 429:
                # 요청 한도 초과 - 재시도 가능한 오류
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # 1초, 2초, 4초 순으로 대기
                    print(f"요청 한도 초과. {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
            
            elif response.status_code >= 500:
                # 서버 오류 - 재시도 가능한 오류
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    print(f"서버 오류 발생. {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"API 서버에 오류가 발생했습니다. (상태코드: {response.status_code})")
            
            else:
                raise Exception(f"API 오류가 발생했습니다. (상태코드: {response.status_code})")
        
        # 7. 네트워크 관련 예외 처리
        except requests.exceptions.Timeout:
            last_error = "요청 시간이 초과되었습니다."
            if attempt < max_retries - 1:
                print(f"타임아웃 발생. 재시도 {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)
                continue
        
        except requests.exceptions.ConnectionError:
            last_error = "네트워크 연결에 실패했습니다."
            if attempt < max_retries - 1:
                print(f"연결 오류 발생. 재시도 {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)
                continue
        
        except requests.exceptions.RequestException as e:
            last_error = f"네트워크 요청 중 오류가 발생했습니다: {str(e)}"
            if attempt < max_retries - 1:
                print(f"요청 오류 발생. 재시도 {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)
                continue
        
        except Exception as e:
            # 재시도 불가능한 오류는 즉시 발생시킴
            error_msg = str(e)
            if any(keyword in error_msg for keyword in ["API 키", "잘못된 요청", "접근 권한", "비어있습니다", "파싱할 수 없습니다"]):
                print("ask_chatgpt 에러:", e)
                raise
            else:
                # 예상치 못한 오류는 재시도
                last_error = str(e)
                if attempt < max_retries - 1:
                    print(f"예상치 못한 오류 발생. 재시도 {attempt + 1}/{max_retries}: {e}")
                    time.sleep(2 ** attempt)
                    continue
    
    # 8. 모든 재시도 실패 시
    final_error = f"최대 재시도 횟수({max_retries})를 초과했습니다."
    if last_error:
        final_error += f" 마지막 오류: {last_error}"
    
    print("ask_chatgpt 에러:", final_error)
    raise Exception(final_error)