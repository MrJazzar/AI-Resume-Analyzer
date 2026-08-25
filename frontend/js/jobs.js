/**
 * jobs.js — job board: list, client-side search across
 * title/company/location/experience/skills, create, and delete.
 */

let ALL_JOBS = [];

function parseSkills(raw) {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed;
  } catch (err) {
    /* not JSON — fall through to comma-split */
  }
  return raw.split(",").map((s) => s.trim()).filter(Boolean);
}

function jobCardHtml(job) {
  const skills = parseSkills(job.required_skills);
  return `
    <div class="card job-card" data-job-id="${job.id}">
      <div class="flex-between" style="align-items:flex-start;">
        <div>
          <div class="job-title">${job.title}</div>
          <div class="job-company">${job.company || "Unlisted company"}</div>
        </div>
        <button class="btn btn-danger-ghost btn-sm" data-delete-job="${job.id}">Delete</button>
      </div>
      <div class="job-meta">
        ${job.location ? `<span>📍 ${job.location}</span>` : ""}
        ${job.experience ? `<span>🧭 ${job.experience}</span>` : ""}
      </div>
      ${job.description ? `<div class="job-desc">${job.description}</div>` : ""}
      ${skills.length ? `<div class="skill-tags">${skills.map((s) => `<span class="chip">${s}</span>`).join("")}</div>` : ""}
    </div>`;
}

function renderJobs(jobs) {
  const grid = document.getElementById("job-grid");
  const empty = document.getElementById("job-empty");
  if (!jobs.length) {
    grid.innerHTML = "";
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";
  grid.innerHTML = jobs.map(jobCardHtml).join("");

  grid.querySelectorAll("[data-delete-job]").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      const id = btn.dataset.deleteJob;
      if (!confirm("Delete this job posting? This can't be undone.")) return;
      btn.disabled = true;
      try {
        await api.del(`/api/jobs/${id}`);
        ALL_JOBS = ALL_JOBS.filter((j) => String(j.id) !== String(id));
        applyFilter();
      } catch (err) {
        alert(err.message);
        btn.disabled = false;
      }
    });
  });
}

function applyFilter() {
  const q = document.getElementById("job-search").value.trim().toLowerCase();
  if (!q) {
    renderJobs(ALL_JOBS);
    return;
  }
  const filtered = ALL_JOBS.filter((job) => {
    const skills = parseSkills(job.required_skills).join(" ").toLowerCase();
    const haystack = [job.title, job.company, job.location, job.experience, skills]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(q);
  });
  renderJobs(filtered);
}

async function loadJobs() {
  const state = document.getElementById("job-state");
  const grid = document.getElementById("job-grid");
  grid.innerHTML = "";
  state.innerHTML = `<div class="loading-inline"><span class="spinner"></span> Loading jobs…</div>`;
  try {
    ALL_JOBS = await api.get("/api/jobs/");
    state.innerHTML = "";
    applyFilter();
  } catch (err) {
    state.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
  }
}

function initCreateForm() {
  const toggleBtn = document.getElementById("toggle-create");
  const form = document.getElementById("create-job-form");
  const cancelBtn = document.getElementById("cancel-create");
  const errorBox = document.getElementById("create-error");

  toggleBtn.addEventListener("click", () => {
    form.style.display = form.style.display === "none" ? "block" : "none";
  });
  cancelBtn.addEventListener("click", () => {
    form.reset();
    errorBox.innerHTML = "";
    form.style.display = "none";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.innerHTML = "";
    const submitBtn = form.querySelector("button[type=submit]");

    const skillsRaw = form.skills.value.trim();
    const payload = {
      title: form.title.value.trim(),
      company: form.company.value.trim() || null,
      description: form.description.value.trim() || null,
      required_skills: skillsRaw ? skillsRaw.split(",").map((s) => s.trim()).filter(Boolean) : null,
      experience: form.experience.value.trim() || null,
      location: form.location.value.trim() || null,
    };

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="loading-inline"><span class="spinner"></span> Posting…</span>`;
    try {
      const job = await api.post("/api/jobs/", payload);
      ALL_JOBS.unshift(job);
      applyFilter();
      form.reset();
      form.style.display = "none";
    } catch (err) {
      errorBox.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Post job";
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  const user = await appUI.requireAuthAndInitShell();
  if (!user) return;

  document.getElementById("job-search").addEventListener("input", applyFilter);
  initCreateForm();
  await loadJobs();
});
