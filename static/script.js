const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");
const quickButtons = document.querySelectorAll(".quick-btn");

// API endpoint
const API_URL = "/api/query";

// Хэрэглэгчийн мессеж нэмэх
function addUserMessage(text) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message user-message";
  messageDiv.innerHTML = `
        <div class="message-content">
            ${escapeHtml(text)}
        </div>
    `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Bot мессеж нэмэх
function addBotMessage(text, isError = false) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message";
  const errorClass = isError ? "error-message" : "";
  messageDiv.innerHTML = `
        <div class="message-content ${errorClass}">
            <strong>AI Туслах:</strong> ${escapeHtml(text)}
        </div>
    `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Loading indicator нэмэх
function addLoadingMessage() {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message";
  messageDiv.id = "loadingMessage";
  messageDiv.innerHTML = `
        <div class="message-content">
            <strong>AI Туслах:</strong> <span class="loading"></span> Бодож байна...
        </div>
    `;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Loading message устгах
function removeLoadingMessage() {
  const loadingMsg = document.getElementById("loadingMessage");
  if (loadingMsg) {
    loadingMsg.remove();
  }
}

// HTML-ээс хамгаалах
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Доош гүйлгэх
function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Асуулт илгээх
async function sendMessage() {
  const question = userInput.value.trim();

  if (!question) {
    return;
  }

  // Хэрэглэгчийн мессеж харуулах
  addUserMessage(question);
  userInput.value = "";
  sendButton.disabled = true;

  // Loading indicator харуулах
  addLoadingMessage();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: question }),
    });

    const data = await response.json();

    removeLoadingMessage();

    if (data.status === "success") {
      addBotMessage(data.answer);
    } else {
      addBotMessage("Уучлаарай, алдаа гарлаа. Дахин оролдоно уу.", true);
    }
  } catch (error) {
    removeLoadingMessage();
    addBotMessage(
      "Холболтын алдаа гарлаа. Сервер ажиллаж байгаа эсэхийг шалгана уу.",
      true
    );
    console.error("Error:", error);
  } finally {
    sendButton.disabled = false;
    userInput.focus();
  }
}

// Enter дарахад илгээх
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Илгээх товч
sendButton.addEventListener("click", sendMessage);

// Түргэн асуултууд
quickButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const query = button.getAttribute("data-query");
    userInput.value = query;
    sendMessage();
  });
});

// Эхлэхэд focus
userInput.focus();
