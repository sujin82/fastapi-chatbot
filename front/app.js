document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading-indicator'); // 로딩 인디케이터 요소 가져오기

    // 메시지를 채팅창에 추가하는 함수
    function appendMessage(senderType, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${senderType}-message`);
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        // 메시지가 추가되면 스크롤을 항상 아래로 내립니다.
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 로딩 인디케이터를 표시하는 함수
    function showLoadingIndicator() {
        loadingIndicator.classList.add('visible');
        chatMessages.scrollTop = chatMessages.scrollHeight; // 스크롤을 하단으로 유지
    }

    // 로딩 인디케이터를 숨기는 함수
    function hideLoadingIndicator() {
        loadingIndicator.classList.remove('visible');
    }

    // 메시지 전송 로직
    sendButton.addEventListener('click', async () => {
        const content = userInput.value.trim();
        if (content === '') return; // 입력값이 없으면 전송하지 않음

        // 1. 사용자 메시지를 채팅창에 표시
        appendMessage('user', content);
        userInput.value = ''; // 입력창 비우기

        // 2. 로딩 인디케이터 표시
        showLoadingIndicator();

        try {
            // 3. 백엔드 API로 메시지 전송 (FastAPI의 /chat/ 엔드포인트)
            // 현재 로그인 상태가 없으므로 userId는 'guest'로 가정합니다.
            const response = await axios.post('http://127.0.0.1:8000/chat/', { // 백엔드 주소 확인 필요
                userId: 'guest', // 실제 사용자 ID 또는 세션 ID를 사용해야 합니다.
                content: content
            });

            // 4. 로딩 인디케이터 숨기기
            hideLoadingIndicator();

            // 5. 챗봇 응답을 채팅창에 표시
            const botMessage = response.data;
            appendMessage('bot', botMessage.content);

        } catch (error) {
            // 4. 로딩 인디케이터 숨기기 (오류 발생 시에도)
            hideLoadingIndicator();
            console.error('챗봇 API 호출 중 오류 발생:', error);
            // 사용자에게 오류 메시지 표시
            appendMessage('bot', '죄송합니다. 챗봇 응답을 가져오는 데 실패했습니다.');

            // FastAPI의 detail 메시지를 콘솔에 출력 (디버깅용)
            if (error.response && error.response.data && error.response.data.detail) {
                console.error('FastAPI 에러 상세:', error.response.data.detail);
            }
        }
    });

    // Enter 키로 메시지 전송
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendButton.click(); // 전송 버튼 클릭 이벤트를 트리거
        }
    });
});