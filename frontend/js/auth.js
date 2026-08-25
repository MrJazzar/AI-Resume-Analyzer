/**
 * auth.js — register / login form handling.
 * Session is a cookie the browser manages automatically; on success we
 * just redirect into the app.
 */

function showFormError(container, message) {
  container.innerHTML = "";
  if (!message) return;
  const el = document.createElement("div");
  el.className = "alert alert-error";
  el.innerHTML = `<span class="alert-icon">⚠</span><span>${message}</span>`;
  container.appendChild(el);
}

function setBusy(button, busy, busyLabel, idleLabel) {
  button.disabled = busy;
  button.textContent = busy ? busyLabel : idleLabel;
}

/** If a session already exists, skip the auth screen. */
async function redirectIfAuthed() {
  try {
    await api.get("/api/auth/me");
    window.location.href = "dashboard.html";
  } catch (err) {
    // no active session — stay on the auth page
  }
}

function initLoginForm() {
  const form = document.getElementById("login-form");
  const errorBox = document.getElementById("form-error");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    showFormError(errorBox, "");

    const button = form.querySelector("button[type=submit]");
    const email = form.email.value.trim();
    const password = form.password.value;

    setBusy(button, true, "Signing in…", "Sign in");
    try {
      await api.post("/api/auth/login", { email, password });
      window.location.href = "dashboard.html";
    } catch (err) {
      showFormError(errorBox, err.message);
      setBusy(button, false, "Signing in…", "Sign in");
    }
  });
}

function initRegisterForm() {
  const form = document.getElementById("register-form");
  const errorBox = document.getElementById("form-error");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    showFormError(errorBox, "");

    const button = form.querySelector("button[type=submit]");
    const name = form.name.value.trim();
    const email = form.email.value.trim();
    const password = form.password.value;
    const confirm = form.confirm.value;

    if (password !== confirm) {
      showFormError(errorBox, "Passwords don't match.");
      return;
    }
    if (password.length < 8) {
      showFormError(errorBox, "Password must be at least 8 characters.");
      return;
    }

    setBusy(button, true, "Creating account…", "Create account");
    try {
      await api.post("/api/auth/register", { name, email, password });
      window.location.href = "dashboard.html";
    } catch (err) {
      showFormError(errorBox, err.message);
      setBusy(button, false, "Creating account…", "Create account");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  redirectIfAuthed();
  initLoginForm();
  initRegisterForm();
});
