document.getElementById("send-btn").addEventListener("click", async () => {
    const inputField = document.getElementById("user-input");
    const message = inputField.value.trim();
    if (!message) return;

    displayMessage("🙋‍♀️ 나", message);
    inputField.value = "";

    try {
        const res = await axios.post("http://localhost:8000/chat/", {
            user_message: message
        });

        const botReply = res.data.bot_message;
        displayMessage("🤖 챗봇", botReply);
    } catch (err) {
        console.error("API 호출 실패:", err);
        displayMessage("❌ 오류", "챗봇 응답에 실패했어요. 다시 시도해 주세요.");
    }
});

function displayMessage(sender, message) {
    const box = document.getElementById("chat-box");
    const msgDiv = document.createElement("div");
    msgDiv.textContent = `${sender}: ${message}`;
    box.appendChild(msgDiv);
    box.scrollTop = box.scrollHeight;
}