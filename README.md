# AI Resume Analyzer

AI Resume Analyzer is a FastAPI application that lets users upload resumes,
extract their text, analyze them with Gemini, compare them with job postings,
and get RAG-based career advice from a local knowledge base. It includes a
static HTML/CSS/JavaScript frontend and a SQLite database for local development.

## Features

- Cookie-based session authentication (no JWT)
- PDF and DOCX resume upload and text extraction
- Structured resume analysis using the Gemini API
- Job posting CRUD operations and skill search
- Resume-to-job matching with deterministic scores and optional Gemini explanations
- Career advice, missing-skill analysis, and learning roadmaps using RAG
- FastAPI Swagger UI and a pytest test suite

## Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — database
- **ChromaDB and sentence-transformers** — semantic search for RAG
- **Gemini REST API** — resume analysis and generated career advice
- **Cookie-based sessions** — server-side sessions stored in the database

## Project structure

The backend, RAG pipeline, job matching, career endpoints, and static frontend
are included in this repository.

```
AI-Resume-Analyzer/
├── app/
│   ├── main.py             # FastAPI app, CORS, routers, and error handlers
│   ├── database.py         # SQLAlchemy engine, sessions, and initialization
│   ├── config.py           # Environment-backed settings
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic request and response schemas
│   ├── routes/             # Auth, resumes, jobs, recommendations, career
│   ├── services/           # Extraction, analysis, matching, and career logic
│   ├── agents/             # Resume analysis agent entry point
│   ├── rag/                # Loader, chunker, embeddings, vector store, generator
│   └── utils/              # Dependencies, security, validators, and exceptions
├── knowledge_base/         # Documents used by the RAG pipeline
├── frontend/               # Static frontend pages, styles, and scripts
├── data/                   # SQLite database, created at runtime
├── uploads/                # Uploaded resume files, ignored by Git
├── tests/                  # pytest suite
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or newer
- Internet access on the first RAG run to download the embedding model
- A Gemini API key for resume analysis and generated career advice

## Setup on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set at least a long `SECRET_KEY`. `AI_API_KEY` is required for
Gemini-backed resume analysis and RAG generation. Deterministic job matching
still works without it.

Always use `python -m pip` and `python -m pytest` after activation so commands
use the project environment rather than the system Python installation.

If PowerShell blocks activation, run this for the current window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run the backend

```powershell
python -m uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive docs are available at
`http://127.0.0.1:8000/docs`, and the health check is at `/health`.

Database tables are created automatically at startup. The default database is
`data/app.db`, and uploaded files are stored in `uploads/`.

## Run the frontend

Keep the backend running, open a second PowerShell window, and serve the static
frontend:

```powershell
cd frontend
python -m http.server 5500
```

Open `http://127.0.0.1:5500/index.html`. The frontend sends requests to
`http://127.0.0.1:8000` and includes the session cookie automatically. If you
use another frontend port, add its exact origin to `ALLOWED_ORIGINS` in `.env`.

## Configuration

`.env.example` contains the supported settings. For local HTTP development,
keep `SESSION_COOKIE_SECURE=false`; set it to `true` only with HTTPS.

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Session security key | required outside tests |
| `DATABASE_URL` | SQLAlchemy database URL | SQLite at `data/app.db` |
| `AI_API_KEY` | Gemini API key | empty |
| `AI_MODEL` | Gemini model name | `gemini-3.6-flash` |
| `ALLOWED_ORIGINS` | Comma-separated frontend origins | ports 3000 and 5173 |
| `SESSION_EXPIRE_MINUTES` | Session lifetime | `1440` |
| `SESSION_COOKIE_SECURE` | HTTPS-only cookie flag | `false` |
| `UPLOAD_DIR` | Resume upload directory | `uploads/` |

## API overview

| Method | Endpoint             | Auth required | Description              |
|--------|-----------------------|:---:|---------------------------|
| POST   | `/api/auth/register`  | No  | Create a new user, starts a session |
| POST   | `/api/auth/login`     | No  | Log in, starts a session |
| POST   | `/api/auth/logout`    | No  | End the current session |
| GET    | `/api/auth/me`        | Yes | Return the current user |
| POST   | `/api/resumes/upload` | Yes | Upload and extract a PDF or DOCX resume |
| GET    | `/api/resumes/`       | Yes | List the current user's resumes |
| GET    | `/api/resumes/{resume_id}` | Yes | Return a resume and its extracted text |
| POST   | `/api/resumes/{resume_id}/analyze` | Yes | Analyze the extracted resume text |
| GET    | `/api/resumes/{resume_id}/analysis` | Yes | Return the saved resume analysis |
| GET    | `/api/jobs/`          | No  | List all job postings |
| POST   | `/api/jobs/`          | Yes | Create a new job posting |
| GET    | `/api/jobs/{id}`      | No  | Retrieve a specific job posting |
| PUT    | `/api/jobs/{id}`      | Yes | Update a specific job posting |
| DELETE | `/api/jobs/{id}`      | Yes | Delete a specific job posting |
| GET    | `/api/jobs/search`    | No  | Search jobs by skill query parameter |
| GET    | `/api/recommendations/{resume_id}` | Yes | List job recommendations ranked by score |
| GET    | `/api/recommendations/{resume_id}/{job_id}` | Yes | Get detailed recommendation match with LLM explanation |
| GET    | `/api/career/`        | Yes | Check career advisor availability |
| GET    | `/api/career/missing-skills/{resume_id}` | Yes | Find missing skills for a target career |
| GET    | `/api/career/roadmap/{resume_id}` | Yes | Generate a learning roadmap |
| GET    | `/api/career/advice/{resume_id}` | Yes | Generate personalized career advice |
| POST   | `/api/career/ask` | Yes | Ask a RAG career question |

Auth uses an `HttpOnly` session cookie (`session_id` by default), not a bearer
token. Browser requests must include credentials, which the included frontend
already does.

### Example: register

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Mo","email":"mo@example.com","password":"SecurePass123"}' \
  -c cookies.txt
```

### Example: fetch current user

```bash
curl http://127.0.0.1:8000/api/auth/me -b cookies.txt
```

## Error responses

All errors return a consistent shape:

```json
{"detail": "User not found"}
```

Handled statuses: `400`, `401`, `403`, `404`, `500` (see `app/utils/exceptions.py`
and the global handlers in `app/main.py`).

## Database schema

- **users** — id, name, email, password_hash, created_at
- **resumes** — id, user_id, filename, file_path, raw_text, created_at
- **jobs** — id, title, company, description, required_skills, experience, location, created_at, updated_at
- **resume_analysis** — id, resume_id, summary, technical_skills, soft_skills, education, experience, projects, created_at
- **sessions** — id (token), user_id, created_at, expires_at *(supports cookie auth)*

## Running tests

```powershell
python -m pytest tests/ -v
```

Tests use an in-memory SQLite database. Most AI paths are mocked, so a real
`AI_API_KEY` is not required to run the suite.

## Common issues

- **`SECRET_KEY is not set`:** copy `.env.example` to `.env` and set `SECRET_KEY`.
- **`No module named sentence_transformers`:** activate `.venv`, then reinstall the requirements.
- **CORS errors:** add the exact frontend origin, such as `http://127.0.0.1:5500`, to `ALLOWED_ORIGINS`.
- **AI analysis returns `503`:** set `AI_API_KEY`; Gemini features need it.
- **Upload errors:** only PDF and DOCX files up to 10 MB are accepted.

## Git workflow

```bash
git checkout -b feature/backend-foundation
git add .
git commit -m "Implement backend foundation, database, and authentication"
git push origin feature/backend-foundation
```

To clone the repository and start from the latest `main`:

```powershell
git clone https://github.com/MrJazzar/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
git checkout main
git pull --ff-only origin main
```
