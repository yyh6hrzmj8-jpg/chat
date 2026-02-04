// Старый интерфейс сохранён. Здесь только «мозги»: подключение к backend + сохранение истории.

const API_BASE = (localStorage.getItem('apiBase') || 'http://127.0.0.1:8000').replace(/\/$/, '');

const STORAGE_KEY = 'chatMessages';
const TOKEN_KEY = 'authToken';
const CREDS_KEY = 'chatCreds';
const SESSION_KEY = 'chatSessionId';

function saveMessages(messages) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
}
function loadMessages() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
}
function clearMessages() {
  localStorage.removeItem(STORAGE_KEY);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function getCreds() {
  try {
    return JSON.parse(localStorage.getItem(CREDS_KEY) || 'null');
  } catch {
    return null;
  }
}
function setCreds(creds) {
  localStorage.setItem(CREDS_KEY, JSON.stringify(creds));
}

function getSessionId() {
  const v = localStorage.getItem(SESSION_KEY);
  return v ? Number(v) : null;
}
function setSessionId(id) {
  localStorage.setItem(SESSION_KEY, String(id));
}
function clearSessionId() {
  localStorage.removeItem(SESSION_KEY);
}

function randomString(len = 10) {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let out = '';
  for (let i = 0; i < len; i++) out += chars[Math.floor(Math.random() * chars.length)];
  return out;
}

async function api(path, { method = 'GET', token, json } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: json ? JSON.stringify(json) : undefined,
  });

  // Пытаемся прочитать json-ошибку
  let data = null;
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) {
    data = await res.json().catch(() => null);
  } else {
    data = await res.text().catch(() => null);
  }

  if (!res.ok) {
    const msg = (data && data.detail) ? data.detail : `HTTP ${res.status}`;
    const err = new Error(msg);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

async function ensureAuth() {
  // Если токен есть — попробуем использовать.
  const existing = getToken();
  if (existing) return existing;

  // Иначе — создаём/берём сохранённые креды и логинимся.
  let creds = getCreds();
  if (!creds) {
    creds = {
      username: `user_${randomString(8)}`,
      password: `p_${randomString(14)}`,
    };
    setCreds(creds);
  }

  // Регистрируем (если уже есть — сервер вернёт 400/409, это ок)
  try {
    await api('/auth/register', { method: 'POST', json: creds });
  } catch (e) {
    // Если пользователь уже существует — продолжаем.
    // Любую другую проблему пробросим.
    const okStatuses = new Set([400, 409]);
    if (!okStatuses.has(e.status)) throw e;
  }

  const login = await api('/auth/login', { method: 'POST', json: creds });
  setToken(login.access_token);
  return login.access_token;
}

async function createSession(token) {
  const out = await api('/chat/session', { method: 'POST', token });
  setSessionId(out.session_id);
  return out.session_id;
}

async function fetchHistory(token, sessionId) {
  return api(`/chat/history/${sessionId}`, { token });
}

async function ensureSession(token) {
  const sid = getSessionId();
  if (!sid) return createSession(token);

  // Проверим, что сессия существует и принадлежит пользователю.
  try {
    await fetchHistory(token, sid);
    return sid;
  } catch (e) {
    if (e.status === 401 || e.status === 403 || e.status === 404) {
      clearSessionId();
      return createSession(token);
    }
    throw e;
  }
}

// UI
const chatWindow = document.getElementById('chatWindow');
const form = document.getElementById('chatForm');
const input = document.getElementById('messageInput');
const typing = document.getElementById('typingIndicator');
const clearBtn = document.getElementById('clearChat');

let messages = loadMessages();
let locked = false;

function addMessage({ author, text }, { persist = true } = {}) {
  const div = document.createElement('div');
  div.className = `message ${author}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  if (persist) {
    messages.push({ author, text });
    saveMessages(messages);
  }
}

function setLocked(v) {
  locked = v;
  input.disabled = v;
}

async function bootstrap() {
  // Рисуем локальную историю сразу (быстро), а потом синхронизируем с сервером.
  messages.forEach(m => addMessage(m, { persist: false }));

  try {
    const token = await ensureAuth();
    const sessionId = await ensureSession(token);

    // Подтянем историю с сервера и перерисуем (источник истины — БД).
    const hist = await fetchHistory(token, sessionId);
    chatWindow.innerHTML = '';

    const normalized = (hist.messages || []).map(m => ({
      author: m.sender,
      text: m.text,
    }));

    normalized.forEach(m => addMessage(m, { persist: false }));
    messages = normalized;
    saveMessages(messages);
  } catch (e) {
    // Если backend не запущен — оставляем локальный режим, но показываем подсказку.
    addMessage({ author: 'bot', text: 'Подсказка: запусти backend (uvicorn). Сейчас работаю в офлайн-режиме.' });
  }
}

async function sendToBackend(text) {
  const token = await ensureAuth();
  const sessionId = await ensureSession(token);
  const out = await api('/chat/message', {
    method: 'POST',
    token,
    json: { session_id: sessionId, text },
  });
  return out.bot_text;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (locked) return;

  const text = input.value.trim();
  if (!text) return;

  addMessage({ author: 'user', text });
  input.value = '';

  setLocked(true);
  typing.style.display = 'block';

  try {
    // Имитация задержки «бот печатает», как было.
    const answerPromise = sendToBackend(text);
    await new Promise(r => setTimeout(r, 1200));
    const answer = await answerPromise;

    addMessage({ author: 'bot', text: answer });
  } catch (e2) {
    addMessage({ author: 'bot', text: 'Ошибка сервера' });
  } finally {
    typing.style.display = 'none';
    setLocked(false);
    input.focus();
  }
});

clearBtn.addEventListener('click', () => {
  chatWindow.innerHTML = '';
  messages = [];
  clearMessages();

  // Создадим новую сессию на сервере при следующем сообщении.
  clearSessionId();
});

bootstrap();
