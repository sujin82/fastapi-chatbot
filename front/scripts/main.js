document.addEventListener('DOMContentLoaded', async () => {
    const userInput = document.getElementById('user-input');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading-indicator');

    // ★★★ 팝업 창 관련 DOM 요소 가져오기 (추가) ★★★
    const loginModal = document.getElementById('login-modal');
    const closeLoginModalButton = document.getElementById('close-login-modal');

    // ★★★ 1. 메시지 박스 관련 코드 (main.js에서 showMessage를 사용한다면 필요) ★★★
    const messageBox = document.getElementById('messageBox'); 
    function showMessage(message, type) {
        if (!messageBox) {
            console.warn("messageBox element not found. Message cannot be displayed.");
            return;
        }
        messageBox.textContent = message;
        messageBox.className = `message-box show ${type}`;
        setTimeout(() => {
            messageBox.classList.remove('show');
            setTimeout(() => {
                messageBox.className = 'message-box';
            }, 300);
        }, 3000);
    }

    function appendMessage(senderType, content) {
        const wrapper = document.createElement('div');
        wrapper.className = senderType === 'user' ? 'flex justify-end' : 'flex justify-start';

        const bubble = document.createElement('div');
        const baseClasses = 'p-3 rounded-xl max-w-xs break-words';

        if (senderType === 'user') {
            bubble.className = `${baseClasses} bg-green-100 text-green-800`;
        } else {
            bubble.className = `${baseClasses} bg-blue-100 text-blue-800`;
        }

        bubble.textContent = content;
        wrapper.appendChild(bubble);
        chatMessages.appendChild(wrapper);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    const loggedOutLinks = document.getElementById('auth-links-logged-out');
    const loggedInLinks = document.getElementById('auth-links-logged-in');
    const usernameDisplay = document.getElementById('username-display');
    const logoutButton = document.getElementById('logout-button');

    let currentUserId = 'guest';
    let currentUsername = '손님';

    async function checkLoginStatusAndUpdateUI() {
        try {
            const response = await fetch('/me');
            if (response.ok) {
                const userData = await response.json();
                currentUserId = userData.username;
                currentUsername = userData.username;

                usernameDisplay.textContent = `${currentUsername}님`;
                loggedInLinks.classList.remove('hidden');
                loggedOutLinks.classList.add('hidden');

                // 로그인 시 팝업 창 숨기기 (혹시 모를 경우를 대비)
                loginModal.classList.add('hidden');

                appendMessage('bot', `어서오세요, ${currentUsername}님. 무엇을 도와드릴까요?`);

            } else {
                console.log("로그인되지 않은 사용자입니다. guest 모드로 진행합니다.");
                
                loggedInLinks.classList.add('hidden');
                loggedOutLinks.classList.remove('hidden');

                // ★★★ 로그인하지 않은 경우 초기 팝업 창 표시 (변경) ★★★
                // chatMessages.innerHTML = ''; // 기존 메시지 초기화 (선택 사항)
                loginModal.classList.remove('hidden'); // 팝업 창 표시
            }
        } catch (error) {
            console.error('로그인 상태 확인 중 오류 발생:', error);
            loggedInLinks.classList.add('hidden');
            loggedOutLinks.classList.remove('hidden');
            
            // 네트워크 오류 시 팝업 창 표시 (변경)
            loginModal.classList.remove('hidden');
            // appendMessage('bot', '죄송합니다. 네트워크 오류로 인해 로그인 상태를 확인할 수 없습니다. (guest 모드)'); // 이제 팝업이 메시지를 대체
            showMessage('네트워크 오류로 로그인 상태를 확인할 수 없습니다. guest 모드로 진행합니다.', 'error');
        }
    }

    function showLoadingIndicator() {
        loadingIndicator.classList.remove('opacity-0', 'invisible');
        loadingIndicator.classList.add('opacity-100', 'visible');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideLoadingIndicator() {
        loadingIndicator.classList.add('opacity-0', 'invisible');
        loadingIndicator.classList.remove('opacity-100', 'visible');
    }

    async function sendMessage(content) {
        // ★★★ 로그인하지 않은 상태에서 대화 시도 시 팝업 띄우기 (변경) ★★★
        if (currentUserId === 'guest') {
            loginModal.classList.remove('hidden'); // 팝업 창 표시
            // showMessage('챗봇과 대화하려면 로그인이 필요합니다.', 'info'); // 이 메시지 대신 팝업이 뜸
            userInput.value = ''; // 입력된 내용 지우기
            return; // 메시지 전송 중단
        }

        appendMessage('user', content);
        showLoadingIndicator();

        try {
            const response = await axios.post('http://127.0.0.1:8000/chat/', {
                userId: currentUserId,
                content: content
            });

            hideLoadingIndicator();
            const botMessage = response.data;
            appendMessage('bot', botMessage.content);
        } catch (error) {
            hideLoadingIndicator();
            console.error('에러:', error);
            const errorMessage = error.response && error.response.data && error.response.data.detail 
                                 ? error.response.data.detail 
                                 : '죄송합니다. 챗봇 응답을 가져오는 데 실패했습니다.';
            
            if (error.response && error.response.status === 401 && currentUserId === 'guest') {
                loginModal.classList.remove('hidden'); // 팝업 창 표시
                // appendMessage('bot', '죄송합니다. 챗봇과 대화하려면 로그인이 필요합니다. 로그인 후에 다시 시도해주세요.'); // 이 메시지 대신 팝업이 뜸
            } else {
                appendMessage('bot', errorMessage);
            }
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const content = userInput.value.trim();
        if (!content) return;
        
        await sendMessage(content); // sendMessage 함수에서 로그인 상태 검사 및 팝업 처리
    });

    if (logoutButton) {
        logoutButton.addEventListener('click', async (e) => {
            e.preventDefault();

            try {
                const logoutResponse = await fetch('/logout', { method: 'POST' });

                if (logoutResponse.ok) {
                    showMessage('👋 로그아웃되었습니다.', 'success');
                    
                    loggedInLinks.classList.add('hidden');
                    loggedOutLinks.classList.remove('hidden');
                    
                    currentUserId = 'guest';
                    currentUsername = '손님';

                    // 로그아웃 시 채팅 메시지 초기화 및 팝업 띄우기
                    chatMessages.innerHTML = ''; 
                    loginModal.classList.remove('hidden'); // 팝업 창 표시

                } else {
                    const errorData = await logoutResponse.json();
                    showMessage(errorData.detail || '로그아웃 중 오류가 발생했습니다.', 'error');
                    console.error('로그아웃 실패:', errorData);
                }
            } catch (error) {
                console.error('로그아웃 네트워크 오류:', error);
                showMessage('네트워크 오류가 발생했습니다. 다시 시도해주세요.', 'error');
            }
        });
    }

    // ★★★ 팝업 닫기 버튼 이벤트 리스너 (추가) ★★★
    if (closeLoginModalButton) {
        closeLoginModalButton.addEventListener('click', () => {
            loginModal.classList.add('hidden'); // 팝업 창 숨기기
        });
    }

    await checkLoginStatusAndUpdateUI();
});