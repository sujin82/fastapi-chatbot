document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');

    // ★ 추가: messageBox 요소 가져오기 (HTML에 이 ID가 있는 div가 있어야 함)
    const messageBox = document.getElementById('messageBox'); 

    // ★ 추가: 메시지 박스를 표시하는 함수 (로그인 페이지와 동일)
    function showMessage(message, type) {
        messageBox.textContent = message;
        // 기존 클래스 제거 후 새로운 클래스 추가 (초기화)
        messageBox.className = `message-box show ${type}`; 
        
        setTimeout(() => {
            messageBox.classList.remove('show');
            // 애니메이션이 끝난 후 클래스 제거 (깔끔한 초기화를 위해)
            setTimeout(() => {
                messageBox.className = 'message-box';
            }, 300); 
        }, 3000); // 3초 후 메시지 숨김
    }

    // 에러 표시 함수 (기존과 동일)
    function showFieldError(fieldId, message) {
        const errorDiv = document.getElementById(fieldId + '-error');
        const inputField = document.getElementById(fieldId);
        
        if (message) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
            inputField.classList.add('border-red-500');
            inputField.classList.remove('border-gray-300');
        } else {
            errorDiv.classList.add('hidden');
            inputField.classList.remove('border-red-500');
            inputField.classList.add('border-gray-300');
        }
    }

    // 모든 에러 메시지 초기화 (기존과 동일)
    function clearAllErrors() {
        const fields = ['username', 'email', 'password', 'confirm-password'];
        fields.forEach(field => showFieldError(field, ''));
    }

    // 비밀번호 확인 유효성 검사 (기존과 동일)
    function validatePasswords() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (confirmPassword && password !== confirmPassword) {
            showFieldError('confirm-password', '비밀번호가 일치하지 않습니다.');
            return false;
        } else {
            showFieldError('confirm-password', '');
            return true;
        }
    }

    // 이메일 유효성 검사 (기존과 동일)
    function validateEmail() {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            showFieldError('email', '올바른 이메일 형식을 입력해주세요.');
            return false;
        } else {
            showFieldError('email', '');
            return true;
        }
    }

    // 비밀번호 길이 검사 (기존과 동일)
    function validatePassword() {
        const password = passwordInput.value;
        
        if (password && password.length < 6) {
            showFieldError('password', '비밀번호는 최소 6자 이상이어야 합니다.');
            return false;
        } else {
            showFieldError('password', '');
            return true;
        }
    }

    // 실시간 유효성 검사 (기존과 동일)
    passwordInput.addEventListener('input', () => {
        validatePassword();
        validatePasswords();
    });
    
    confirmPasswordInput.addEventListener('input', validatePasswords);
    emailInput.addEventListener('blur', validateEmail);

    // 회원가입 폼 제출 처리
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearAllErrors(); // 필드별 에러 초기화
        
        // ★ 추가: messageBox 메시지도 초기화 (이전 메시지가 남아있을 수 있으므로)
        messageBox.classList.remove('show', 'success', 'error'); 
        messageBox.className = 'message-box'; // 초기화

        // 입력값 가져오기
        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        let hasError = false;

        // 필드별 유효성 검사
        if (!username) {
            showFieldError('username', '이름을 입력해주세요.');
            hasError = true;
        }

        if (!email) {
            showFieldError('email', '이메일을 입력해주세요.');
            hasError = true;
        } else if (!validateEmail()) {
            hasError = true;
        }

        if (!password) {
            showFieldError('password', '비밀번호를 입력해주세요.');
            hasError = true;
        } else if (!validatePassword()) {
            hasError = true;
        }

        if (!confirmPassword) {
            showFieldError('confirm-password', '비밀번호 확인을 입력해주세요.');
            hasError = true;
        } else if (!validatePasswords()) {
            hasError = true;
        }

        if (hasError) {
            // ★ 변경: 필드 에러가 있으면 상단 메시지 박스에는 아무것도 띄우지 않음
            return;
        }

        try {
            // 백엔드 API로 회원가입 요청
            const response = await axios.post('http://127.0.0.1:8000/register', {
                username: username,
                email: email,
                password: password
            });

            // ★ 변경: showSuccessMessage 대신 showMessage 사용
            showMessage('회원가입이 성공적으로 완료되었습니다!', 'success');
            
            // 폼 초기화
            registerForm.reset();
            clearAllErrors(); // 필드별 에러 초기화 (필요시)

            setTimeout(() => {
                window.location.href = '/'; // 메인 페이지로 이동
            }, 3000); // 3초 후 이동
            
        } catch (error) {
            console.error('회원가입 중 오류 발생:', error);

            // 서버 에러 처리
            if (error.response && error.response.data) {
                const errorData = error.response.data;
                
                // 특정 필드 에러인 경우 (기존과 동일)
                if (errorData.field) {
                    showFieldError(errorData.field, errorData.message || errorData.detail);
                    // ★ 추가: 필드 에러가 있으면 상단 메시지 박스에는 상세 에러 메시지 띄우지 않음.
                    // 대신, 일반적인 "회원가입 실패" 메시지를 띄우거나 아무것도 띄우지 않을 수 있습니다.
                    // 여기서는 필드 에러는 필드 아래에, 그 외의 에러는 상단에 띄우도록 처리합니다.
                    showMessage('회원가입에 실패했습니다. 입력값을 확인해주세요.', 'error');

                } else {
                    // ★ 변경: 일반적인 에러 메시지는 showMessage를 통해 상단에 표시
                    let errorMessage = '회원가입 중 오류가 발생했습니다. 다시 시도해주세요.';
                    if (errorData.detail) {
                        errorMessage = errorData.detail;
                    } else if (errorData.message) {
                        errorMessage = errorData.message;
                    }
                    showMessage(errorMessage, 'error');
                }
            } else {
                // 네트워크 오류 또는 알 수 없는 오류
                showMessage('네트워크 오류가 발생했습니다. 다시 시도해주세요.', 'error');
            }

            // 상세 에러 로그 (개발용)
            if (error.response) {
                console.error('에러 상태:', error.response.status);
                console.error('에러 데이터:', error.response.data);
            }
        }
    });
});