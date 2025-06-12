document.addEventListener('DOMContentLoaded', async () => {
    const userInput = document.getElementById('user-input');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading-indicator');

    const loginModal = document.getElementById('login-modal');
    const closeLoginModalButton = document.getElementById('close-login-modal');

    const showHistoryBtn = document.getElementById('showHistoryBtn'); 
    
    const clearHistoryButton = document.getElementById('clear-history-button');

    const messageBox = document.getElementById('messageBox'); 

    // null 체크 추가
    if (!showHistoryBtn) {
        console.warn("showHistoryBtn 요소를 찾을 수 없습니다. HTML에서 id='showHistoryBtn' 요소가 존재하는지 확인해주세요.");
    }

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

    // ★★★ 새로운 함수: 채팅 기록의 존재 여부만 확인 ★★★
    async function checkIfHistoryExists() {
        try {
            const response = await fetch('/chat/history');
            if (response.ok) {
                const data = await response.json();
                return (data.history && data.history.length > 0);
            }
            return false;
        } catch (error) {
            console.error('채팅 기록 존재 여부 확인 중 오류:', error);
            return false;
        }
    }

    // ★★★ 채팅 기록 로드 함수 (버튼 클릭 시 화면에 출력) ★★★
    // 이 함수는 기록 유무에 따라 showHistoryBtn의 가시성을 조절합니다.
    async function loadChatHistory(clearCurrentChat = false) { 
        let hasHistory = false; 
        try {
            const response = await fetch('/chat/history');
            if (response.ok) {
                const data = await response.json();
                const messages = data.history || []; 
                
                if (clearCurrentChat) { // 버튼 클릭 시에만 기존 메시지 초기화
                    chatMessages.innerHTML = '';
                }
                
                if (messages.length > 0) {
                    hasHistory = true; 
                    messages.forEach(message => {
                        appendMessage(message.senderType, message.content);
                    });
                    console.log(`${messages.length}개의 채팅 기록을 복원했습니다.`);
                    showMessage(`${messages.length}개의 이전 대화를 복원했습니다.`, 'info'); 
                } else {
                    console.log('이전 채팅 기록이 없습니다.');
                    showMessage('이전 채팅 기록이 없습니다.', 'info'); 
                }
                
            } else if (response.status === 401) {
                console.log('채팅 기록을 불러오려면 로그인이 필요합니다.');
                showMessage('로그인이 필요합니다. 다시 로그인해주세요.', 'error'); 
            } else {
                console.error('채팅 기록을 불러올 수 없습니다:', response.status);
                showMessage('채팅 기록을 불러오는 데 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('채팅 기록 로드 중 오류:', error);
            showMessage('채팅 기록 로드 중 네트워크 오류가 발생했습니다.', 'error');
        } finally {
            // ★★★ 변경: 히스토리 불러오기 버튼 클릭으로 로드했을 경우 버튼 숨김 ★★★
            if (showHistoryBtn) {
                if (clearCurrentChat) { // '히스토리 불러오기' 버튼 클릭으로 호출된 경우
                    showHistoryBtn.classList.add('hidden'); // 무조건 숨깁니다.
                } else { // 로그인 시 초기 확인 등 다른 경우
                    if (hasHistory) { // 기록이 존재하면 보이게 유지
                        showHistoryBtn.classList.remove('hidden'); 
                    } else { // 기록이 없으면 숨김
                        showHistoryBtn.classList.add('hidden'); 
                    }
                }
            }
        }
        return hasHistory; 
    }

    async function clearChatHistory() {
        try {
            const response = await fetch('/chat/history', { method: 'DELETE' });
            if (response.ok) {
                chatMessages.innerHTML = ''; 
                showMessage('채팅 기록이 성공적으로 삭제되었습니다.', 'success');
                if (showHistoryBtn) {
                    showHistoryBtn.classList.add('hidden'); 
                }
                appendMessage('ai', `새로운 대화를 시작해주세요, ${currentUsername}님.`);
            } else {
                const errorData = await response.json();
                showMessage(errorData.detail || '채팅 기록 삭제에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('채팅 기록 삭제 중 오류:', error);
            showMessage('채팅 기록 삭제 중 오류가 발생했습니다.', 'error');
        }
    }

    const loggedOutLinks = document.getElementById('auth-links-logged-out');
    const loggedInLinks = document.getElementById('auth-links-logged-in');
    const logoutButton = document.getElementById('logout-button');

    let currentUserId = 'guest'; 
    let currentUsername = '손님';

    async function checkLoginStatusAndUpdateUI() {
        try {
            const response = await fetch('/me');
            if (response.ok) {
                const userData = await response.json();
                currentUserId = String(userData.id); 
                currentUsername = userData.username;

                if (loggedInLinks) loggedInLinks.classList.remove('hidden');
                if (loggedOutLinks) loggedOutLinks.classList.add('hidden');

                if (loginModal) loginModal.classList.add('hidden');

                // ★★★ 변경: 로그인 시 히스토리 로드 대신 존재 여부만 확인 ★★★
                const historyExists = await checkIfHistoryExists(); 
                
                // 히스토리가 있을 때만 버튼 활성화
                if (showHistoryBtn) {
                    if (historyExists) {
                        showHistoryBtn.classList.remove('hidden'); // 기록이 있으면 보이게
                    } else {
                        showHistoryBtn.classList.add('hidden'); // 기록이 없으면 숨기게
                    }
                }

                // 채팅 메시지 영역이 비어있을 때만 웰컴 메시지 표시
                if (chatMessages && chatMessages.children.length === 0) { 
                    appendMessage('ai', `어서오세요, ${currentUsername}님. 무엇을 도와드릴까요?`);
                }

            } else {
                
                if (loggedInLinks) loggedInLinks.classList.add('hidden');
                if (loggedOutLinks) loggedOutLinks.classList.remove('hidden');

                if (loginModal) loginModal.classList.remove('hidden');

                // 로그인되지 않은 상태에서는 '히스토리 불러오기' 버튼 숨김
                if (showHistoryBtn) {
                    showHistoryBtn.classList.add('hidden');
                }
            }
        } catch (error) {
            console.error('로그인 상태 확인 중 오류 발생:', error);
            if (loggedInLinks) loggedInLinks.classList.add('hidden');
            if (loggedOutLinks) loggedOutLinks.classList.remove('hidden');
            
            if (loginModal) loginModal.classList.remove('hidden');
            showMessage('네트워크 오류로 로그인 상태를 확인할 수 없습니다. guest 모드로 진행합니다.', 'error');
            // 오류 발생 시에도 '히스토리 불러오기' 버튼 숨김
            if (showHistoryBtn) {
                showHistoryBtn.classList.add('hidden');
            }
        }
    }

    function showLoadingIndicator() {
        if (loadingIndicator) {
            loadingIndicator.classList.remove('opacity-0', 'invisible');
            loadingIndicator.classList.add('opacity-100', 'visible');
        }
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function hideLoadingIndicator() {
        if (loadingIndicator) {
            loadingIndicator.classList.add('opacity-0', 'invisible');
            loadingIndicator.classList.remove('opacity-100', 'visible');
        }
    }

    function disableInput() {
        if (userInput) {
            userInput.disabled = true;
            userInput.placeholder = '응답을 기다리는 중...';
        }
    }

    function enableInput() {
        if (userInput) {
            userInput.disabled = false;
            userInput.placeholder = '메시지를 입력하세요...';
            userInput.focus();
        }
    }

    async function sendMessage(content) {
        if (currentUserId === 'guest') {
            if (loginModal) loginModal.classList.remove('hidden');
            if (userInput) userInput.value = '';
            return;
        }

        disableInput();
        appendMessage('user', content);
        showLoadingIndicator();

        try {
            const response = await axios.post('http://127.0.0.1:8000/chat/', {
                userId: currentUserId, 
                content: content
            });

            hideLoadingIndicator();
            
            const botResponseData = response.data; 

            console.log('서버로부터 받은 botResponseData:', botResponseData);
            console.log('botResponseData의 타입:', typeof botResponseData);
            console.log('botResponseData.content 속성:', botResponseData ? botResponseData.content : 'N/A');

            let actualBotContent = '챗봇 응답을 처리할 수 없습니다.'; 

            if (botResponseData && typeof botResponseData === 'object' && botResponseData.content) {
                actualBotContent = botResponseData.content;
            } else if (typeof botResponseData === 'string') {
                try {
                    const parsed = JSON.parse(botResponseData);
                    if (parsed && typeof parsed === 'object' && parsed.content) {
                        actualBotContent = parsed.content; 
                    } else {
                        actualBotContent = botResponseData; 
                    }
                } catch (e) {
                    actualBotContent = botResponseData; 
                }
            } else {
                actualBotContent = '챗봇 응답 형식 오류.';
            }

            appendMessage('ai', actualBotContent);
            
            // ★★★ 새 메시지 전송 후 '히스토리 불러오기' 버튼 활성화 ★★★
            // 메시지를 전송했으므로 이제 기록이 있을 수 있습니다.
            if (showHistoryBtn) { 
                 showHistoryBtn.classList.remove('hidden'); 
            }

        } catch (error) {
            hideLoadingIndicator();
            console.error('에러:', error);
            const errorMessage = error.response && error.response.data && error.response.data.detail 
                                 ? error.response.data.detail 
                                 : '죄송합니다. 챗봇 응답을 가져오는 데 실패했습니다.';
            
            if (error.response && error.response.status === 401 && currentUserId === 'guest') {
                if (loginModal) loginModal.classList.remove('hidden');
            } else {
                appendMessage('ai', errorMessage);
            }
        } finally {
            enableInput();
        }
    }

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const content = userInput ? userInput.value.trim() : '';
            if (!content) return;

            if (userInput) userInput.value = '';
            await sendMessage(content);
        });
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', async (e) => {
            e.preventDefault();

            try {
                const logoutResponse = await fetch('/logout', { method: 'POST' });

                if (logoutResponse.ok) {
                    showMessage('👋 로그아웃되었습니다.', 'success');
                    
                    if (loggedInLinks) loggedInLinks.classList.add('hidden');
                    if (loggedOutLinks) loggedOutLinks.classList.remove('hidden');
                    
                    currentUserId = 'guest';
                    currentUsername = '손님';

                    if (chatMessages) chatMessages.innerHTML = ''; 
                    if (loginModal) loginModal.classList.remove('hidden');

                    if (showHistoryBtn) {
                        showHistoryBtn.classList.add('hidden');
                    }

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

    if (clearHistoryButton) {
        clearHistoryButton.addEventListener('click', async (e) => {
            e.preventDefault();
            if (confirm('정말로 모든 채팅 기록을 삭제하시겠습니까?')) {
                await clearChatHistory();
            }
        });
    }
    
    if (showHistoryBtn) {
        showHistoryBtn.addEventListener('click', async () => {
            await loadChatHistory(true); 
        });
    }

    if (closeLoginModalButton) {
        closeLoginModalButton.addEventListener('click', () => {
            if (loginModal) loginModal.classList.add('hidden');
        });
    }

    await checkLoginStatusAndUpdateUI();
});