/**
 * career.js — Career Advisor UI: missing skills / roadmap / advice tabs
 * backed by the RAG pipeline, plus a free-form "ask" chat.
 *
 * The advisor's underlying generator always returns JSON shaped like
 * {"answer": "...", "sources": [...]}, but some prompts also ask the
 * model to emit extra structured fields (missing_skills, learning_path,
 * etc). renderCareerPayload() renders whichever fields are present so
 * the UI works either way.
 */

let RESUMES_CACHE = [];

function listSection(title, arr) {
  if (!arr || !arr.length) return "";
  return `<div class="analysis-section" style="margin-bottom:14px;">
    <h4>${title}</h4>
    <ul class="list-plain">${arr.map((i) => `<li>${i}</li>`).join("")}</ul>
  </div>`;
}

function renderCareerPayload(container, data) {
  if (!data) {
    container.innerHTML = "";
    return;
  }
  let html = "";
  if (data.answer) html += `<div class="explanation" style="margin-bottom:14px;">${data.answer}</div>`;
  html += listSection("Required skills", data.required_skills);
  html += listSection("Missing skills", data.missing_skills);
  html += listSection("Learning path", data.learning_path);
  html += listSection("Resources", data.resources);
  html += listSection("Recommended projects", data.projects);
  html += listSection("Certifications", data.certifications);
  html += listSection("Resume improvements", data.resume_improvements);

  if (!html) {
    html = `<pre class="mono" style="white-space:pre-wrap;font-size:12px;background:var(--surface-sunken);padding:12px;border-radius:8px;">${JSON.stringify(
      data,
      null,
      2
    )}</pre>`;
  }
  if (data.sources && data.sources.length) {
    html += `<div class="text-muted" style="margin-top:6px;">Sources: ${data.sources.join(", ")}</div>`;
  }
  container.innerHTML = html;
}

async function populateResumeSelect() {
  const select = document.getElementById("resume-select");
  try {
    RESUMES_CACHE = await api.get("/api/resumes/");
    if (!RESUMES_CACHE.length) {
      document.getElementById("career-empty").style.display = "block";
      document.getElementById("career-body").style.display = "none";
      return false;
    }
    RESUMES_CACHE.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).forEach((r) => {
      const opt = document.createElement("option");
      opt.value = r.id;
      opt.textContent = r.filename;
      select.appendChild(opt);
    });
    return true;
  } catch (err) {
    document.getElementById("career-state").innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
    return false;
  }
}

function currentResumeId() {
  return document.getElementById("resume-select").value;
}
function currentTargetCareer() {
  return document.getElementById("target-career").value.trim();
}

async function runTab(tab) {
  const target = currentTargetCareer();
  const resumeId = currentResumeId();
  const output = document.getElementById(`tab-output-${tab}`);
  const state = document.getElementById("career-state");
  state.innerHTML = "";

  if (!target) {
    state.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>Enter a target career first (e.g. "AI Engineer").</span></div>`;
    return;
  }

  const endpoints = {
    "missing-skills": `/api/career/missing-skills/${resumeId}`,
    roadmap: `/api/career/roadmap/${resumeId}`,
    advice: `/api/career/advice/${resumeId}`,
  };

  const loadingLabel = {
    "missing-skills": "Finding missing skills…",
    roadmap: "Building your roadmap…",
    advice: "Getting career advice…",
  };

  output.innerHTML = `<div class="loading-inline"><span class="spinner"></span> ${loadingLabel[tab]}</div>`;
  try {
    const data = await api.get(endpoints[tab], { target_career: target });
    renderCareerPayload(output, data);
  } catch (err) {
    const msg = err.status === 503 ? "AI analysis isn't configured on the server yet (missing AI_API_KEY)." : err.message;
    output.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${msg}</span></div>`;
  }
}

function initTabs() {
  const tabs = document.querySelectorAll(".career-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      document.querySelectorAll(".tab-panel").forEach((p) => (p.style.display = "none"));
      const panel = document.getElementById(`panel-${tab.dataset.tab}`);
      panel.style.display = "block";

      if (tab.dataset.tab !== "ask") {
        const output = document.getElementById(`tab-output-${tab.dataset.tab}`);
        if (!output.dataset.loaded) runTab(tab.dataset.tab);
      }
    });
  });

  document.querySelectorAll("[data-run-tab]").forEach((btn) => {
    btn.addEventListener("click", () => runTab(btn.dataset.runTab));
  });
}

function appendBubble(role, html) {
  const thread = document.getElementById("ask-thread");
  const bubble = document.createElement("div");
  bubble.className = `ask-bubble ${role}`;
  bubble.innerHTML = html;
  thread.appendChild(bubble);
  thread.scrollTop = thread.scrollHeight;
}

function initAsk() {
  const form = document.getElementById("ask-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("ask-input");
    const question = input.value.trim();
    if (!question) return;

    appendBubble("user", question);
    input.value = "";

    const loadingId = `loading-${Date.now()}`;
    appendBubble("assistant", `<span id="${loadingId}" class="loading-inline"><span class="spinner"></span> Thinking…</span>`);

    try {
      const data = await api.post("/api/career/ask", {
        question,
        resume_id: Number(currentResumeId()) || null,
        target_career: currentTargetCareer() || null,
      });
      const bubbleEl = document.getElementById(loadingId).closest(".ask-bubble");
      let html = data.answer || "No answer generated.";
      if (data.sources && data.sources.length) {
        html += `<div class="sources">Sources: ${data.sources.join(", ")}</div>`;
      }
      bubbleEl.innerHTML = html;
    } catch (err) {
      const bubbleEl = document.getElementById(loadingId).closest(".ask-bubble");
      const msg = err.status === 503 ? "AI analysis isn't configured on the server yet (missing AI_API_KEY)." : err.message;
      bubbleEl.innerHTML = `<span style="color:var(--danger)">⚠ ${msg}</span>`;
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const user = await appUI.requireAuthAndInitShell();
  if (!user) return;

  const ok = await populateResumeSelect();
  if (!ok) return;

  initTabs();
  initAsk();
});
