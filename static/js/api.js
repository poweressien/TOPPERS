/* ═══════════════════════════════════════════
   TOPPERS — API Helper
   All fetch calls go through here.
═══════════════════════════════════════════ */
const API = '/api/v1';

// ── Token management ──────────────────────
function getToken()   { return localStorage.getItem('access_token'); }
function getRefresh() { return localStorage.getItem('refresh_token'); }
function getUser()    { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; }
function isLoggedIn() { return !!getToken(); }

function setAuth(data) {
  localStorage.setItem('access_token',  data.tokens ? data.tokens.access  : data.access);
  localStorage.setItem('refresh_token', data.tokens ? data.tokens.refresh : data.refresh);
  if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
}

function clearTokens() {
  ['access_token','refresh_token','user'].forEach(k => localStorage.removeItem(k));
}

function requireAuth() {
  if (!isLoggedIn()) { window.location.href = '/login/'; }
}
function redirectIfLoggedIn() {
  if (isLoggedIn()) { window.location.href = '/dashboard/'; }
}

// ── Core fetch wrapper ────────────────────
async function apiFetch(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...opts.headers };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res = await fetch(API + path, { ...opts, headers });

  // Auto-refresh on 401
  if (res.status === 401 && getRefresh()) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${getToken()}`;
      res = await fetch(API + path, { ...opts, headers });
    } else {
      clearTokens();
      window.location.href = '/login/';
      return null;
    }
  }
  return res;
}

async function tryRefresh() {
  try {
    const res = await fetch(`${API}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: getRefresh() }),
    });
    if (res.ok) {
      const d = await res.json();
      localStorage.setItem('access_token', d.access);
      return true;
    }
    return false;
  } catch { return false; }
}

// ── Convenience methods ───────────────────
async function apiGet(path)         { return apiFetch(path); }
async function apiPost(path, body)  { return apiFetch(path, { method:'POST', body: JSON.stringify(body) }); }
async function apiPatch(path, body) { return apiFetch(path, { method:'PATCH', body: JSON.stringify(body) }); }

// ── Toast notifications ───────────────────
function toast(msg, type = 'info', duration = 3500) {
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${icons[type]||''}</span> <span>${msg}</span>`;
  const c = document.getElementById('toastContainer');
  if (c) c.appendChild(el);
  setTimeout(() => el.remove(), duration);
}

// ── Loading state helpers ─────────────────
function setLoading(btn, loading, text = 'Loading...') {
  if (!btn) return;
  if (loading) {
    btn.dataset.origText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ${text}`;
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.origText || text;
  }
}

// ── Format helpers ────────────────────────
function fmtNum(n) { return Number(n || 0).toLocaleString(); }
function fmtDate(d) { return new Date(d).toLocaleDateString('en-NG', { day:'numeric', month:'short', year:'numeric' }); }
