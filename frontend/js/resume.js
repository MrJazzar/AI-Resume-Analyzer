/**
 * resume.js — upload flow, resume list, and analysis rendering.
 */

const MAX_FILE_BYTES = 10 * 1024 * 1024; // 10 MB, matches backend limit
const ALLOWED_EXT = [".pdf", ".docx"];

function validateFile(file) {
  const name = file.name.toLowerCase();
  const okExt = ALLOWED_EXT.some((ext) => name.endsWith(ext));
  if (!okExt) return "Only PDF and DOCX files are supported.";
  if (file.size === 0) return "This file is empty.";
  if (file.size > MAX_FILE_BYTES) return "File is too large — the limit is 10 MB.";
  return null;
}

function fmtDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

/* ---------------------------------------------------------------- */
/* Upload                                                            */
/* ---------------------------------------------------------------- */
function initUpload() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const pickedBox = document.getElementById("file-picked");
  const uploadBtn = document.getElementById("upload-btn");
  const uploadError = document.getElementById("upload-error");
  if (!dropzone) return;

  let selectedFile = null;

  function showPicked(file) {
    selectedFile = file;
    pickedBox.style.display = "flex";
    pickedBox.querySelector(".fp-name").textContent = file.name;
    pickedBox.querySelector(".fp-size").textContent = `${(file.size / 1024).toFixed(0)} KB`;
    uploadBtn.disabled = false;
  }

  function handleFiles(files) {
    uploadError.innerHTML = "";
    const file = files[0];
    if (!file) return;
    const err = validateFile(file);
    if (err) {
      uploadError.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err}</span></div>`;
      uploadBtn.disabled = true;
      selectedFile = null;
      return;
    }
    showPicked(file);
  }

  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => handleFiles(e.target.files));

  ["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("drag-over");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("drag-over");
    })
  );
  dropzone.addEventListener("drop", (e) => handleFiles(e.dataTransfer.files));

  uploadBtn.addEventListener("click", async () => {
    if (!selectedFile) return;
    uploadError.innerHTML = "";
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `<span class="loading-inline"><span class="spinner"></span> Uploading…</span>`;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const resume = await api.upload("/api/resumes/upload", formData);
      window.location.href = `resume.html?id=${resume.id}`;
    } catch (err) {
      uploadError.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
      uploadBtn.disabled = false;
      uploadBtn.textContent = "Upload & extract";
    }
  });
}

/* ---------------------------------------------------------------- */
/* Resume list                                                       */
/* ---------------------------------------------------------------- */
async function loadResumeList(activeId) {
  const box = document.getElementById("resume-list");
  try {
    const resumes = await api.get("/api/resumes/");
    if (!resumes.length) {
      box.innerHTML = `<div class="state-block" style="padding:24px 8px;">
        <div class="state-title">No resumes yet</div>
        <div class="state-sub">Upload your first resume above to get started.</div>
      </div>`;
      return;
    }
    box.innerHTML = "";
    resumes
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .forEach((r) => {
        const item = el(`
          <a href="resume.html?id=${r.id}" class="resume-list-item" style="text-decoration:none;color:inherit;">
            <div>
              <div class="r-name">${r.filename}</div>
              <div class="r-date">Uploaded ${fmtDate(r.created_at)}</div>
            </div>
            <span class="chip">${String(r.id) === String(activeId) ? "Viewing" : "View →"}</span>
          </a>`);
        box.appendChild(item);
      });
  } catch (err) {
    box.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
  }
}

/* ---------------------------------------------------------------- */
/* Resume detail + analysis                                          */
/* ---------------------------------------------------------------- */
function renderAnalysis(analysis) {
  const box = document.getElementById("analysis-box");

  const skillTags = (skills) =>
    skills && skills.length
      ? `<div class="skill-tags">${skills.map((s) => `<span class="chip">${s}</span>`).join("")}</div>`
      : `<div class="text-muted">None detected.</div>`;

  const timeline = (items, primaryKeys, subKeys, descKey) => {
    if (!items || !items.length) return `<div class="text-muted">None detected.</div>`;
    return items
      .map((it) => {
        const primary = primaryKeys.map((k) => it[k]).find(Boolean) || "—";
        const sub = subKeys.map((k) => it[k]).filter(Boolean).join(" · ");
        const desc = descKey && it[descKey] ? it[descKey] : "";
        return `<div class="timeline-entry">
          <div class="t-title">${primary}</div>
          ${sub ? `<div class="t-sub">${sub}</div>` : ""}
          ${desc ? `<div class="t-desc">${desc}</div>` : ""}
        </div>`;
      })
      .join("");
  };

  box.innerHTML = `
    <div class="analysis-section">
      <h4>Summary</h4>
      <p>${analysis.summary || "No summary generated."}</p>
    </div>
    <div class="analysis-grid">
      <div class="analysis-section">
        <h4>Technical skills</h4>
        ${skillTags(analysis.technical_skills)}
      </div>
      <div class="analysis-section">
        <h4>Soft skills</h4>
        ${skillTags(analysis.soft_skills)}
      </div>
      <div class="analysis-section">
        <h4>Education</h4>
        ${timeline(analysis.education, ["degree", "major", "university"], ["university", "graduation_year"], null)}
      </div>
      <div class="analysis-section">
        <h4>Experience</h4>
        ${timeline(analysis.experience, ["position", "title"], ["company", "duration"], "responsibilities")}
      </div>
    </div>
    <div class="analysis-section" style="margin-top:18px;">
      <h4>Projects</h4>
      ${timeline(analysis.projects, ["name", "project_name"], ["technologies"], "description")}
    </div>
  `;
}

async function loadResumeDetail(id) {
  const detailCard = document.getElementById("detail-card");
  const detailState = document.getElementById("detail-state");
  const analyzeBtn = document.getElementById("analyze-btn");

  if (!id) {
    detailCard.style.display = "none";
    return;
  }
  detailCard.style.display = "block";
  detailState.innerHTML = `<div class="loading-inline"><span class="spinner"></span> Loading resume…</div>`;

  let resume;
  try {
    resume = await api.get(`/api/resumes/${id}`);
  } catch (err) {
    detailState.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${err.message}</span></div>`;
    return;
  }

  document.getElementById("detail-filename").textContent = resume.filename;
  document.getElementById("detail-date").textContent = `Uploaded ${fmtDate(resume.created_at)}`;
  document.getElementById("raw-text-box").textContent = resume.raw_text || "No extracted text available.";
  detailState.innerHTML = "";

  async function tryLoadAnalysis() {
    try {
      const analysis = await api.get(`/api/resumes/${id}/analysis`);
      document.getElementById("analysis-box").style.display = "block";
      document.getElementById("no-analysis-box").style.display = "none";
      renderAnalysis(analysis);
    } catch (err) {
      document.getElementById("analysis-box").style.display = "none";
      document.getElementById("no-analysis-box").style.display = "block";
    }
  }

  analyzeBtn.onclick = async () => {
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<span class="loading-inline"><span class="spinner"></span> Analyzing resume…</span>`;
    detailState.innerHTML = "";
    try {
      await api.post(`/api/resumes/${id}/analyze`);
      await tryLoadAnalysis();
    } catch (err) {
      const msg =
        err.status === 503 && err.message.includes("quota")
          ? err.message
          : err.status === 503
          ? "AI analysis isn't configured on the server yet (missing AI_API_KEY)."
          : err.message;
      detailState.innerHTML = `<div class="alert alert-error"><span class="alert-icon">⚠</span><span>${msg}</span></div>`;
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analyze resume";
    }
  };

  await tryLoadAnalysis();
}

document.addEventListener("DOMContentLoaded", async () => {
  const user = await appUI.requireAuthAndInitShell();
  if (!user) return;

  initUpload();
  const params = new URLSearchParams(window.location.search);
  const activeId = params.get("id");
  await loadResumeList(activeId);
  await loadResumeDetail(activeId);
});
