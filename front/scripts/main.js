
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const chatForm = document.getElementById('chat-form'); // form 요소 선택
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading-indicator');

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
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 로딩 인디케이터를 숨기는 함수
    function hideLoadingIndicator() {
        loadingIndicator.classList.remove('visible');
    }

    // 메시지 전송 함수
    async function sendMessage(content) {
        // 1. 사용자 메시지를 채팅창에 표시
        appendMessage('user', content);

        // 2. 로딩 인디케이터 표시
        showLoadingIndicator();

        try {
            // 3. 백엔드 API로 메시지 전송
            const response = await axios.post('http://127.0.0.1:8000/chat/', {
                userId: 'guest',
                content: content
            });

            // 4. 로딩 인디케이터 숨기기
            hideLoadingIndicator();

            // 5. 챗봇 응답을 채팅창에 표시
            const botMessage = response.data;
            appendMessage('bot', botMessage.content);

        } catch (error) {
            // 로딩 인디케이터 숨기기 (오류 발생 시에도)
            hideLoadingIndicator();
            console.error('챗봇 API 호출 중 오류 발생:', error);
            
            // 사용자에게 오류 메시지 표시
            appendMessage('bot', '죄송합니다. 챗봇 응답을 가져오는 데 실패했습니다.');

            // FastAPI의 detail 메시지를 콘솔에 출력 (디버깅용)
            if (error.response && error.response.data && error.response.data.detail) {
                console.error('FastAPI 에러 상세:', error.response.data.detail);
            }
        }
    }

    // Form submit 이벤트 리스너 (핵심 변경 부분!)
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // 페이지 새로고침 방지
        
        const content = userInput.value.trim();
        if (content === '') return; // 입력값이 없으면 전송하지 않음

        userInput.value = ''; // 입력창 비우기
        
        await sendMessage(content); // 메시지 전송
    });
});