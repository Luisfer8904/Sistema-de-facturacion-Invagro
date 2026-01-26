const CHAT_STORAGE_KEY = "invagro_chat_history";
const CHAT_LIMIT = 200;

function openChat() {
  const overlay = document.getElementById("chatOverlay");
  if (!overlay) return;
  overlay.classList.add("open");
  overlay.setAttribute("aria-hidden", "false");
  document.querySelectorAll(".chat-trigger").forEach((el) => {
    el.classList.add("active");
    el.setAttribute("aria-pressed", "true");
  });
  const input = document.getElementById("chatInput");
  if (input) {
    input.focus();
  }
}

function closeChat() {
  const overlay = document.getElementById("chatOverlay");
  if (!overlay) return;
  overlay.classList.remove("open");
  overlay.setAttribute("aria-hidden", "true");
  document.querySelectorAll(".chat-trigger").forEach((el) => {
    el.classList.remove("active");
    el.setAttribute("aria-pressed", "false");
  });
}

function loadChatHistory() {
  try {
    const raw = localStorage.getItem(CHAT_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    return [];
  }
}

function saveChatHistory(history) {
  try {
    const trimmed = history.slice(-CHAT_LIMIT);
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(trimmed));
  } catch (err) {
    // ignore storage failures
  }
}

function renderChatHistory() {
  const container = document.getElementById("chatMessages");
  if (!container) return;
  container.innerHTML = "";
  const history = loadChatHistory();
  history.forEach((item) => {
    appendMessage(item.role, item.content, false);
  });
  container.scrollTop = container.scrollHeight;
}

function appendMessage(role, content, persist = true) {
  const container = document.getElementById("chatMessages");
  if (!container) return;
  const message = document.createElement("div");
  message.className = `chat-message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble";
  bubble.textContent = content;
  message.appendChild(bubble);
  container.appendChild(message);
  container.scrollTop = container.scrollHeight;

  if (persist) {
    const history = loadChatHistory();
    history.push({ role, content, ts: new Date().toISOString() });
    saveChatHistory(history);
  }
}

function setLoadingState(isLoading) {
  const input = document.getElementById("chatInput");
  const button = document.querySelector(".chat-input button");
  if (input) input.disabled = isLoading;
  if (button) button.disabled = isLoading;
}

function sendMessage(event) {
  if (event) event.preventDefault();
  const input = document.getElementById("chatInput");
  if (!input) return false;
  const message = input.value.trim();
  if (!message) return false;

  appendMessage("user", message, true);
  input.value = "";
  setLoadingState(true);

  fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  })
    .then(async (resp) => {
      const data = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        const errorText = data.error || data.detail || `Error ${resp.status}`;
        appendMessage("assistant", errorText, true);
        return;
      }
      appendMessage("assistant", data.reply || "Listo.", true);
    })
    .catch(() => {
      appendMessage("assistant", "Error de red. Intenta de nuevo.", true);
    })
    .finally(() => {
      setLoadingState(false);
    });

  return false;
}

function initChatWidget() {
  renderChatHistory();
  const overlay = document.getElementById("chatOverlay");
  if (overlay) {
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) {
        closeChat();
      }
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeChat();
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initChatWidget);
} else {
  initChatWidget();
}
