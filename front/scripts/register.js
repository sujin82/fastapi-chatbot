document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const registerButton = document.getElementById('register-button');


    // 메시지 표시 함수
    function showMessage(message, type = 'error') {
        // 기존 메시지 제거
        const existingMessage = document.querySelector('.success-message, .error-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // 새 메시지 생성
        const messageDiv = document.createElement('div');
        messageDiv.className = type === 'success' ? 'success-message' : 'error-message';
        messageDiv.textContent = message;

        // 폼 위에 메시지 삽입
        registerForm.insertBefore(messageDiv, registerForm.firstChild);

        // 3초 후 메시지 자동 제거
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    // 비밀번호 확인 유효성 검사
    function validatePasswords() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (confirmPassword && password !== confirmPassword) {
            confirmPasswordInput.setCustomValidity('비밀번호가 일치하지 않습니다.');
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    }

    // 비밀번호 입력 시 실시간 검증
    passwordInput.addEventListener('input', validatePasswords);
    confirmPasswordInput.addEventListener('input', validatePasswords);

    // 회원가입 폼 제출 처리
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 입력값 가져오기
        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // 기본 유효성 검사
        if (!username || !email || !password || !confirmPassword) {
            showMessage('모든 필드를 입력해주세요.');
            return;
        }

        if (password !== confirmPassword) {
            showMessage('비밀번호가 일치하지 않습니다.');
            return;
        }

        if (password.length < 6) {
            showMessage('비밀번호는 최소 6자 이상이어야 합니다.');
            return;
        }


        try {
            // 백엔드 API로 회원가입 요청
            const response = await axios.post('http://127.0.0.1:8000/register', {
                username: username,
                email: email,
                password: password
            });

            // 성공 처리
            showMessage('회원가입이 성공적으로 완료되었습니다!', 'success');
            
            // 폼 초기화
            registerForm.reset();

            setTimeout(() => {
                window.location.href = '/';
            }, 3000);

        } catch (error) {
            console.error('회원가입 중 오류 발생:', error);

            // 에러 메시지 처리
            let errorMessage = '회원가입 중 오류가 발생했습니다.';
            
            if (error.response && error.response.data) {
                if (error.response.data.detail) {
                    errorMessage = error.response.data.detail;
                } else if (error.response.data.message) {
                    errorMessage = error.response.data.message;
                }
            }

            showMessage(errorMessage);

            // 상세 에러 로그 (개발용)
            if (error.response) {
                console.error('에러 상태:', error.response.status);
                console.error('에러 데이터:', error.response.data);
            }
        }
    });

    // 이메일 형식 실시간 검증
    emailInput.addEventListener('blur', () => {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            emailInput.setCustomValidity('올바른 이메일 형식을 입력해주세요.');
        } else {
            emailInput.setCustomValidity('');
        }
    });
});