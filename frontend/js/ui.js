/**
 * ui.js — shared app-shell behaviour used on every authenticated page
 * (sidebar, mobile nav toggle, current-user display, logout).
 */

function initials(name) {
  if (!name) return "?";
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join("");
}

function highlightActiveNav() {
  const current = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".sidebar nav a[data-page]").forEach((link) => {
    if (link.dataset.page === current) link.classList.add("active");
  });
}

function initMobileNav() {
  const toggle = document.querySelector("[data-nav-toggle]");
  const sidebar = document.querySelector(".sidebar");
  const backdrop = document.querySelector(".sidebar-backdrop");
  if (!toggle || !sidebar) return;

  const close = () => {
    sidebar.classList.remove("open");
    backdrop && backdrop.classList.remove("open");
  };

  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    backdrop && backdrop.classList.toggle("open");
  });
  backdrop && backdrop.addEventListener("click", close);
  sidebar.querySelectorAll("nav a").forEach((a) => a.addEventListener("click", close));
}

function bindLogout() {
  document.querySelectorAll("[data-logout]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      try {
        await api.post("/api/auth/logout");
      } catch (err) {
        // even if the request fails, drop the client back to login
      } finally {
        window.location.href = "login.html";
      }
    });
  });
}

/**
 * Populates sidebar user info and guards the page: redirects to login.html
 * if there is no active session. Call this at the top of every protected page.
 * Returns the current user object once resolved.
 */
async function requireAuthAndInitShell() {
  highlightActiveNav();
  initMobileNav();
  bindLogout();

  try {
    const user = await api.get("/api/auth/me");
    document.querySelectorAll("[data-user-name]").forEach((el) => (el.textContent = user.name));
    document.querySelectorAll("[data-user-email]").forEach((el) => (el.textContent = user.email));
    document.querySelectorAll("[data-user-initials]").forEach((el) => (el.textContent = initials(user.name)));
    return user;
  } catch (err) {
    window.location.href = "login.html";
    return null;
  }
}

window.appUI = { requireAuthAndInitShell, initials };
