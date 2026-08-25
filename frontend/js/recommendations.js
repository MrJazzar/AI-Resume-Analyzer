/**
 * recommendations.js — pick a resume, list ranked job matches,
 * and drill into a detailed LLM explanation per job.
 */

let CURRENT_RESUME_ID = null;

function scoreColor(score) {
  if (score >= 75) return "var(--primary)";
  if (score >= 45) return "var(--accent)";
  return "var(--danger)";
}

async function populateResumeSelect() {
  const select = document.getElementById("resume-select");
  const params = new URLSearchParams(window.location.search);
  const preselect = params.get("resume_id");

  try {
    const resumes = await api.get("/api/resumes/");
    if (!resumes.length) {
      document.getElementById("rec-state").innerHTML = `<div class="state-block">
        <div class="state-title">No resumes yet</div>
        <div class="state-sub">Upload a resume first to get job recommendations.</div>
        <a href="resume.html" class="btn btn-primary btn-sm" style="margin-top:14px;">Upload resume</a>
      </div>`;
      document.getElementById("rec-controls").style.display = "none";
      return null;
    }

    resumes
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .forEach((r) => {
        const opt = document.createElement("option");
        opt.value = r.id;
        opt.textContent = r.filename;
        select.appendChild(opt);
      });

    const initial = preselect && resumes.some((r) => String(r.id) === preselect) ? preselect : resumes[0].id;
    select.value = initial;
    return initial;
  } catch (err) {
    document.getElementById("rec-state").innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
    return null;
  }
}

function recCardHtml(rec) {
  return `
    <div class="card rec-card" data-job-id="${rec.job_id}">
      <div class="gauge" style="--gauge-val:${rec.score}; --gauge-color:${scoreColor(rec.score)};">
        <span class="gauge-value">${rec.score}</span>
      </div>
      <div class="rec-body">
        <div class="rec-title">${rec.title}</div>
        <div class="rec-company">${rec.company || "Unlisted company"}</div>
        <div class="skill-tags">
          ${rec.matched_skills.map((s) => `<span class="chip chip-match">${s}</span>`).join("")}
          ${rec.missing_skills.map((s) => `<span class="chip chip-missing">${s}</span>`).join("")}
        </div>
        <div class="rec-detail-panel" style="display:none;"></div>
      </div>
      <button class="btn btn-ghost btn-sm" data-toggle-detail>Why this match?</button>
    </div>`;
}

function renderRecs(recs) {
  const box = document.getElementById("rec-list");
  const state = document.getElementById("rec-state");
  if (!recs.length) {
    box.innerHTML = "";
    state.innerHTML = `<div class="state-block">
      <div class="state-title">No matches yet</div>
      <div class="state-sub">Add some job postings, then analyze this resume to see match scores.</div>
    </div>`;
    return;
  }
  state.innerHTML = "";
  box.innerHTML = recs
    .sort((a, b) => b.score - a.score)
    .map(recCardHtml)
    .join("");

  box.querySelectorAll("[data-toggle-detail]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const card = btn.closest(".rec-card");
      const panel = card.querySelector(".rec-detail-panel");
      const jobId = card.dataset.jobId;

      if (panel.style.display === "block") {
        panel.style.display = "none";
        btn.textContent = "Why this match?";
        return;
      }

      panel.style.display = "block";
      btn.textContent = "Hide explanation";

      if (panel.dataset.loaded === "true") return;
      panel.innerHTML = `<div class="loading-inline"><span class="spinner"></span> Generating explanation…</div>`;

      try {
        const detail = await api.get(`/api/recommendations/${CURRENT_RESUME_ID}/${jobId}`);
        panel.innerHTML = `<div class="explanation">${detail.explanation || "No explanation available."}</div>`;
        panel.dataset.loaded = "true";
      } catch (err) {
        panel.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
      }
    });
  });
}

async function loadRecommendations(resumeId) {
  CURRENT_RESUME_ID = resumeId;
  const state = document.getElementById("rec-state");
  const box = document.getElementById("rec-list");
  box.innerHTML = "";
  state.innerHTML = `<div class="loading-inline"><span class="spinner"></span> Finding best jobs…</div>`;

  try {
    const recs = await api.get(`/api/recommendations/${resumeId}`);
    renderRecs(recs);
  } catch (err) {
    state.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const user = await appUI.requireAuthAndInitShell();
  if (!user) return;

  const initial = await populateResumeSelect();
  if (!initial) return;

  await loadRecommendations(initial);

  document.getElementById("resume-select").addEventListener("change", (e) => {
    loadRecommendations(e.target.value);
  });
});
