// ── ESTADO ──────────────────────────────────────────────────
let isProcessing    = false;
let recognition     = null;
let isRecording     = false;
let currentAudio    = null;
let alwaysListening = false;
let pendingImages   = [];   // Array de {data: base64, media_type: string, objectUrl: string}

// ── ELEMENTOS ───────────────────────────────────────────────
const chatMessages     = document.getElementById("chatMessages");
const textInput        = document.getElementById("textInput");
const statusDot        = document.getElementById("statusDot");
const statusText       = document.getElementById("statusText");
const avatarCore       = document.getElementById("avatarCore");
const waveform         = document.getElementById("waveform");
const micBtn           = document.getElementById("micBtn");
const toolEntries      = document.getElementById("toolEntries");
const imagePreviewArea = document.getElementById("imagePreviewArea");
const imageFileInput   = document.getElementById("imageFileInput");

// ── RELÓGIO ──────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById("timeDisplay").textContent =
    now.toLocaleTimeString("pt-PT", { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();

// ── STATUS ───────────────────────────────────────────────────
function setStatus(state) {
  const states = {
    ready:     { text: "Pronto",         dot: "",          avatar: "" },
    listening: { text: "A ouvir...",     dot: "listening", avatar: "listening" },
    thinking:  { text: "A processar...", dot: "busy",      avatar: "thinking" },
    speaking:  { text: "A falar...",     dot: "busy",      avatar: "speaking" },
  };
  const s = states[state] || states.ready;
  statusText.textContent = s.text;
  statusDot.className    = "status-dot " + s.dot;
  avatarCore.className   = "avatar-core " + s.avatar;
}

// ── MENSAGENS ────────────────────────────────────────────────
function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  const initial = role === "jarvis" ? "J" : "V";
  div.innerHTML = `
    <div class="msg-avatar">${initial}</div>
    <div class="msg-bubble">${escapeHtml(text)}</div>
  `;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

function createJarvisBubble(modelName) {
  const div = document.createElement("div");
  div.className = "message jarvis";
  const badgeClass = modelName === "Haiku" ? "badge-haiku"
                   : modelName === "Opus"  ? "badge-opus"
                   : "badge-sonnet";
  div.innerHTML = `
    <div class="msg-avatar">J</div>
    <div class="msg-bubble">
      <span class="model-badge ${badgeClass}">${modelName || "Sonnet"}</span>
      <span class="bubble-text"></span>
    </div>
  `;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

function appendTokenToBubble(bubbleDiv, token) {
  const span = bubbleDiv.querySelector(".bubble-text");
  if (span) {
    // Converte \n para <br> progressivamente
    span.innerHTML += escapeHtml(token).replace(/\n/g, "<br>");
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

function showTyping() {
  const div = document.createElement("div");
  div.className = "message jarvis typing";
  div.id = "typingIndicator";
  div.innerHTML = `
    <div class="msg-avatar">J</div>
    <div class="msg-bubble">
      <div class="dot"></div><div class="dot"></div><div class="dot"></div>
    </div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ── TOOL LOG ─────────────────────────────────────────────────
function logTool(tool, result) {
  const div = document.createElement("div");
  div.className = "tool-entry";
  div.innerHTML = `<span class="tool-name">⚙ ${escapeHtml(tool)}</span><br>${escapeHtml(result)}`;
  toolEntries.insertBefore(div, toolEntries.firstChild);
  while (toolEntries.children.length > 8) {
    toolEntries.removeChild(toolEntries.lastChild);
  }
}

// ── ÁUDIO ────────────────────────────────────────────────────
async function playReply(text) {
  try {
    setStatus("speaking");
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }

    const resp = await fetch("/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    if (!resp.ok) { setStatus("ready"); return; }

    const blob = await resp.blob();
    const url  = URL.createObjectURL(blob);
    currentAudio = new Audio(url);
    currentAudio.onended = () => {
      URL.revokeObjectURL(url);
      currentAudio = null;
      setStatus("ready");
      // Modo sempre a ouvir: reinicia escuta após JARVIS terminar de falar
      if (alwaysListening && !isProcessing) {
        setTimeout(() => {
          if (alwaysListening && !isProcessing && !isRecording) {
            toggleMic();
          }
        }, 500);
      }
    };
    currentAudio.onerror = () => {
      setStatus("ready");
      if (alwaysListening && !isProcessing) {
        setTimeout(() => { if (alwaysListening && !isProcessing) toggleMic(); }, 500);
      }
    };
    await currentAudio.play();
  } catch {
    setStatus("ready");
    if (alwaysListening && !isProcessing) {
      setTimeout(() => { if (alwaysListening && !isProcessing) toggleMic(); }, 500);
    }
  }
}

// ── IMAGENS ──────────────────────────────────────────────────
function triggerImageUpload() {
  imageFileInput.value = "";
  imageFileInput.click();
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files || []);
  files.forEach(file => addImagePreview(file));
}

function addImagePreview(file) {
  if (!file || !file.type.startsWith("image/")) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    const base64Full = e.target.result; // data:image/jpeg;base64,....
    const parts = base64Full.split(",");
    const mediaType = parts[0].replace("data:", "").replace(";base64", "");
    const b64data   = parts[1];

    const imgObj = { data: b64data, media_type: mediaType, objectUrl: base64Full };
    pendingImages.push(imgObj);

    // Cria thumbnail no preview
    const item = document.createElement("div");
    item.className = "image-preview-item";
    const idx = pendingImages.length - 1;
    item.dataset.index = idx;
    item.innerHTML = `
      <img src="${base64Full}" alt="imagem">
      <button class="image-preview-remove" onclick="removeImagePreview(${idx})" title="Remover">×</button>
    `;
    imagePreviewArea.appendChild(item);
  };
  reader.readAsDataURL(file);
}

function removeImagePreview(index) {
  pendingImages[index] = null;
  const item = imagePreviewArea.querySelector(`[data-index="${index}"]`);
  if (item) item.remove();
}

function clearImagePreviews() {
  pendingImages = [];
  imagePreviewArea.innerHTML = "";
}

// Colar imagem do clipboard
document.addEventListener("paste", (e) => {
  const items = e.clipboardData ? e.clipboardData.items : [];
  for (const item of items) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) addImagePreview(file);
    }
  }
});

// ── ENVIAR MENSAGEM (STREAMING) ──────────────────────────────
async function sendMessage(text) {
  const msg = (text || textInput.value).trim();
  if (!msg || isProcessing) return;

  textInput.value = "";
  isProcessing = true;
  document.querySelector(".btn-send").disabled = true;

  // Mostra mensagem do utilizador
  addMessage("user", msg);

  // Recolhe imagens pendentes
  const imagesToSend = pendingImages.filter(Boolean);
  clearImagePreviews();

  // Mostra indicador typing
  showTyping();
  setStatus("thinking");

  // Prepara body
  const body = { message: msg };
  if (imagesToSend.length > 0) {
    body.images = imagesToSend.map(i => ({ data: i.data, media_type: i.media_type }));
  }

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      removeTyping();
      addMessage("jarvis", "Erro de ligação ao servidor.");
      setStatus("ready");
      isProcessing = false;
      document.querySelector(".btn-send").disabled = false;
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let jarvisBubble = null;
    let fullText = "";
    let modelName = "Sonnet";

    removeTyping();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Processa linhas SSE completas
      const lines = buffer.split("\n");
      buffer = lines.pop(); // guarda linha incompleta

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;

        let event;
        try { event = JSON.parse(jsonStr); } catch { continue; }

        if (event.type === "model") {
          modelName = event.model || "Sonnet";
          // Cria bubble agora com o badge correto
          if (!jarvisBubble) {
            jarvisBubble = createJarvisBubble(modelName);
          }
        }

        else if (event.type === "token") {
          if (!jarvisBubble) {
            jarvisBubble = createJarvisBubble(modelName);
          }
          fullText += event.text;
          appendTokenToBubble(jarvisBubble, event.text);
        }

        else if (event.type === "tool") {
          logTool(event.name, event.result || "");
        }

        else if (event.type === "error") {
          if (!jarvisBubble) {
            jarvisBubble = createJarvisBubble(modelName);
          }
          const errText = event.text || "Erro desconhecido.";
          appendTokenToBubble(jarvisBubble, errText);
          fullText = errText;
        }

        else if (event.type === "done") {
          fullText = event.full_text || fullText;
          if (event.model) {
            modelName = event.model;
            // Atualiza badge se necessário
            if (jarvisBubble) {
              const badge = jarvisBubble.querySelector(".model-badge");
              if (badge) {
                badge.textContent = modelName;
                badge.className = "model-badge " + (
                  modelName === "Haiku" ? "badge-haiku" :
                  modelName === "Opus"  ? "badge-opus"  : "badge-sonnet"
                );
              }
            }
          }
        }
      }
    }

    // TTS com o texto completo
    if (fullText.trim()) {
      await playReply(fullText.trim());
    } else {
      setStatus("ready");
      if (alwaysListening && !isProcessing) {
        setTimeout(() => { if (alwaysListening && !isProcessing) toggleMic(); }, 500);
      }
    }

  } catch (err) {
    removeTyping();
    addMessage("jarvis", "Erro de ligação ao servidor.");
    setStatus("ready");
    console.error("Erro sendMessage:", err);
  }

  isProcessing = false;
  document.querySelector(".btn-send").disabled = false;
}

// ── MICROFONE (Web Speech API) ───────────────────────────────
function toggleMic() {
  if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
    alert("Microfone não suportado neste browser.\nUsa Chrome ou Edge.");
    return;
  }

  if (isRecording) {
    stopMic();
    return;
  }

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = "pt-PT";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isRecording = true;
    micBtn.classList.add("recording");
    waveform.classList.add("active");
    setStatus("listening");
    // Para o áudio do JARVIS se estiver a falar
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
  };

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    textInput.value = transcript;
    stopMic();
    setTimeout(() => sendMessage(transcript), 300);
  };

  recognition.onerror = (e) => {
    console.warn("STT error:", e.error);
    stopMic();
    // Se sempre a ouvir e o erro não for fatal, tenta novamente
    if (alwaysListening && e.error !== "not-allowed" && !isProcessing) {
      setTimeout(() => { if (alwaysListening && !isProcessing) toggleMic(); }, 1500);
    }
  };

  recognition.onend = () => stopMic();

  recognition.start();
}

function stopMic() {
  if (recognition) { recognition.stop(); recognition = null; }
  isRecording = false;
  micBtn.classList.remove("recording");
  waveform.classList.remove("active");
  if (!isProcessing) setStatus("ready");
}

// ── SEMPRE A OUVIR ───────────────────────────────────────────
function toggleAlwaysListening() {
  alwaysListening = !alwaysListening;
  const btn = document.getElementById("alwaysListenBtn");
  btn.classList.toggle("active", alwaysListening);

  if (alwaysListening) {
    // Começa a ouvir imediatamente se não estiver a processar
    if (!isProcessing && !isRecording) {
      toggleMic();
    }
  } else {
    // Para de ouvir se estiver a gravar
    if (isRecording) {
      stopMic();
    }
  }
}

// ── RESET ────────────────────────────────────────────────────
async function resetChat() {
  await fetch("/reset", { method: "POST" });
  chatMessages.innerHTML = `
    <div class="message jarvis">
      <div class="msg-avatar">J</div>
      <div class="msg-bubble">Conversa reiniciada. Como posso ajudar, Sr. Vitor?</div>
    </div>`;
  toolEntries.innerHTML = "";
  clearImagePreviews();
}

// ── INIT ─────────────────────────────────────────────────────
textInput.focus();
