// DOMContentLoaded 이벤트 리스너를 사용하여 문서가 완전히 로드된 후에 스크립트가 실행되도록 합니다.
document.addEventListener('DOMContentLoaded', () => {
    // 1. 필요한 DOM 요소 가져오기
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // --- 중요한 변경사항: 사용자 ID 설정 ---
    const CURRENT_USER_ID = "guest_user_123"; 

    // 헬퍼 함수: 메시지를 채팅창에 추가하는 함수 (이전과 동일)
    function addMessage(sender, message) {
        if (!chatMessages) {
            console.error('Error: chat-messages element not found. Cannot add message.');
            return;
        }

        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        
        if (sender === 'user') {
            messageElement.classList.add('user-message');
            messageElement.textContent = `나: ${message}`;
        } else if (sender === 'ai') { 
            messageElement.classList.add('bot-message');
            messageElement.textContent = `챗봇: ${message}`;
        } else {
            console.warn(`Unknown sender type: ${sender}. Using default styling.`);
            messageElement.textContent = `${sender}: ${message}`;
        }

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- 백엔드 API 호출 함수 (Axios 사용) ---
    async function sendMessageToBackend(message) {
        try {
            // FastAPI 백엔드 서버의 주소와 챗 엔드포인트
            const backendUrl = 'http://127.0.0.1:8000/chat/'; 

            // FastAPI의 `/chat` 엔드포인트는 `ChatMessage` Pydantic 모델을 기대합니다.
            // Axios는 객체를 직접 body로 전달하면 자동으로 JSON.stringify 처리해줍니다.
            const payload = {
                userId: CURRENT_USER_ID, 
                senderType: "user",      
                content: message         
            };

            // axios.post()를 사용하여 POST 요청을 보냅니다.
            // 첫 번째 인자는 URL, 두 번째 인자는 요청 본문(payload) 데이터입니다.
            // 세 번째 인자는 config 객체로, 헤더 등을 설정할 수 있습니다.
            const response = await axios.post(backendUrl, payload, {
                headers: {
                    'Content-Type': 'application/json' 
                }
            });

            // Axios는 응답 데이터를 자동으로 JSON으로 파싱하여 `response.data`에 담아줍니다.
            // HTTP 상태 코드가 2xx가 아닌 경우 (예: 4xx, 5xx) Axios는 자동으로 Promise를 reject합니다.
            return response.data.content; // 챗봇의 실제 응답 내용

        } catch (error) {
            // Axios의 에러 처리는 fetch보다 직관적입니다.
            // 에러 객체에 `response`, `request`, `message` 속성이 포함될 수 있습니다.
            if (error.response) {
                // 서버가 응답했으나, 상태 코드가 2xx 범위 밖인 경우
                console.error('백엔드 통신 중 에러 발생 (서버 응답 오류):', error.response.status, error.response.data);
                return `죄송합니다. 챗봇 서버에서 오류가 발생했습니다: ${error.response.data.detail || error.response.statusText}`;
            } else if (error.request) {
                // 요청은 보냈으나, 응답을 받지 못한 경우 (예: 네트워크 오류, 서버 다운)
                console.error('백엔드 통신 중 에러 발생 (요청 전송 오류):', error.request);
                return `죄송합니다. 챗봇 서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.`;
            } else {
                // 그 외의 에러 (예: 요청 설정 중 문제 발생)
                console.error('백엔드 통신 중 에러 발생 (알 수 없는 오류):', error.message);
                return `죄송합니다. 알 수 없는 오류가 발생했습니다: ${error.message}`;
            }
        }
    }

    // 메시지 전송 로직을 포함하는 메인 함수 (이전과 동일하지만, 내부에서 sendMessageToBackend가 변경됨)
    async function sendMessage() {
        const message = userInput.value.trim();

        if (message) {
            addMessage('user', message);
            userInput.value = '';

            const loadingMessageElement = document.createElement('div');
            loadingMessageElement.classList.add('message', 'bot-message');
            loadingMessageElement.textContent = '챗봇: 챗봇이 응답을 생성 중입니다...';
            chatMessages.appendChild(loadingMessageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const botReply = await sendMessageToBackend(message);

                if (chatMessages.lastChild === loadingMessageElement) {
                    chatMessages.removeChild(loadingMessageElement);
                }
                
                addMessage('ai', botReply);

            } catch (error) {
                console.error('챗봇 응답 처리 중 에러 발생:', error);
                
                if (chatMessages.lastChild === loadingMessageElement) {
                    chatMessages.removeChild(loadingMessageElement);
                }
                addMessage('ai', "죄송합니다. 챗봇 응답을 받지 못했습니다.");
            }
        }
    }

    // 2. "전송" 버튼 클릭 이벤트 리스너 등록
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    } else {
        console.error('Error: send-button element not found. Check your index.html ID.');
    }

    // 3. Enter 키 입력 이벤트 리스너 등록
    if (userInput) {
        userInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    } else {
        console.error('Error: user-input element not found. Check your index.html ID.');
    }
});
