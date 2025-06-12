document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading-indicator');

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

    // ✅ 초기 인사 메시지
    appendMessage('bot', '어서오세요. 무엇을 도와드릴까요?');

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
        appendMessage('user', content);
        showLoadingIndicator();

        try {
            const response = await axios.post('http://127.0.0.1:8000/chat/', {
                userId: 'guest',
                content: content
            });

            hideLoadingIndicator();
            const botMessage = response.data;
            appendMessage('bot', botMessage.content);
        } catch (error) {
            hideLoadingIndicator();
            console.error('에러:', error);
            appendMessage('bot', '죄송합니다. 챗봇 응답을 가져오는 데 실패했습니다.');
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const content = userInput.value.trim();
        if (!content) return;
        userInput.value = '';
        await sendMessage(content);
    });
});