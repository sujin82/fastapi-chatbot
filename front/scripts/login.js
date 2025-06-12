
const loginForm = document.getElementById('loginForm');
const messageBox = document.getElementById('messageBox');

// 메시지 박스를 표시하는 함수
function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.className = `message-box show ${type}`; // 클래스 추가
    // 3초 후 메시지 박스 숨김
    setTimeout(() => {
        messageBox.classList.remove('show');
        // 메시지 박스가 완전히 사라진 후 클래스 제거 (애니메이션이 끝난 후)
        setTimeout(() => {
            messageBox.className = 'message-box';
        }, 300);
    }, 3000);
}

loginForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // 폼 기본 제출 동작 막기

    const username = loginForm.username.value;
    const password = loginForm.password.value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok) { // HTTP 상태 코드가 200번대인 경우 (성공)
            showMessage(data.message || '로그인 성공!', 'success');
            console.log('로그인 성공:', data);
            // 로그인 성공 후 리디렉션 (예: 메인 페이지 또는 대시보드)
            // 실제 애플리케이션에서는 JWT 토큰이나 세션 쿠키를 처리한 후 리디렉션
            setTimeout(() => {
                window.location.href = '/'; // 메인 페이지로 이동
            }, 1500); // 메시지 보여주고 1.5초 후 이동
        } else { // HTTP 상태 코드가 200번대가 아닌 경우 (실패)
            showMessage(data.detail || '로그인 실패. 사용자 이름 또는 비밀번호를 확인해주세요.', 'error');
            console.error('로그인 실패:', data);
        }
    } catch (error) {
        console.error('네트워크 오류:', error);
        showMessage('네트워크 오류가 발생했습니다. 다시 시도해주세요.', 'error');
    }
});