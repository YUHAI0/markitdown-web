const THEME_KEY = "markitdown-web:theme";
const loginPanel = document.querySelector("#login-panel");
const statsPanel = document.querySelector("#stats-panel");
const loginForm = document.querySelector("#login-form");
const passwordInput = document.querySelector("#password-input");
const loginError = document.querySelector("#login-error");
const logoutButton = document.querySelector("#logout-button");
const adminLabel = document.querySelector("#admin-label");
const usersValue = document.querySelector("#users-value");
const documentsValue = document.querySelector("#documents-value");
const themeToggle = document.querySelector("#theme-toggle");

function getStoredTheme() {
  try {
    return localStorage.getItem(THEME_KEY);
  } catch {
    return null;
  }
}

function setStoredTheme(value) {
  try {
    localStorage.setItem(THEME_KEY, value);
  } catch {
    /* storage may be blocked; ignore */
  }
}

function resolveInitialTheme() {
  const stored = getStoredTheme();
  if (stored === "light" || stored === "dark") return stored;
  return "light";
}

function applyTheme(theme) {
  const root = document.documentElement;
  if (theme === "dark") {
    root.setAttribute("data-theme", "dark");
  } else {
    root.setAttribute("data-theme", "light");
  }
  if (themeToggle) {
    themeToggle.setAttribute(
      "aria-label",
      theme === "dark" ? "切换到浅色主题" : "切换到深色主题"
    );
  }
}

function showLogin(message) {
  loginPanel.hidden = false;
  statsPanel.hidden = true;
  logoutButton.hidden = true;
  adminLabel.hidden = false;
  loginError.hidden = !message;
  if (message) loginError.textContent = message;
}

function showStats(payload) {
  loginPanel.hidden = true;
  statsPanel.hidden = false;
  logoutButton.hidden = false;
  adminLabel.hidden = true;
  loginError.hidden = true;
  usersValue.textContent = Number(payload.unique_users).toLocaleString("zh-CN");
  documentsValue.textContent = Number(payload.documents).toLocaleString("zh-CN");
}

async function loadStats() {
  const response = await fetch("/api/admin/stats");
  if (response.status === 401) {
    showLogin();
    return;
  }
  if (!response.ok) {
    showLogin("无法读取统计");
    return;
  }
  showStats(await response.json());
}

async function submitLogin(event) {
  event.preventDefault();
  loginError.hidden = true;
  const response = await fetch("/admin/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: passwordInput.value }),
  });
  if (!response.ok) {
    showLogin("密码错误");
    passwordInput.focus();
    return;
  }
  passwordInput.value = "";
  await loadStats();
}

async function logout() {
  await fetch("/admin/logout", { method: "POST" });
  showLogin();
}

applyTheme(resolveInitialTheme());

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    setStoredTheme(next);
  });
}

loginForm.addEventListener("submit", submitLogin);
logoutButton.addEventListener("click", logout);
loadStats();
