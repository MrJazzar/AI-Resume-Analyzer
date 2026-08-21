# AI Resume Analyzer

Backend foundation for the AI Resume Analyzer team project — FastAPI + SQLite,
with database models, cookie-based session authentication, and a basic API
structure ready for the rest of the team to build on.

## Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — database
- **Passlib (bcrypt)** — password hashing
- **Cookie-based sessions** — server-side sessions stored in the DB, sent to
  the client as an `HttpOnly` cookie (not JWT)

## Project structure

This repository contains the Member 1 foundation and the Member 2 resume
upload, extraction, and AI analysis implementation. Remaining folders are
scaffolds for later team members.

```
AI-Resume-Analyzer/
├── app/
│   ├── main.py            # FastAPI app, CORS, routers, error handlers
│   ├── database.py        # SQLAlchemy engine/session/Base
│   ├── config.py          # Settings loaded from .env
│   ├── models/            # SQLAlchemy models (user, resume, job, resume_analysis, session)
│   ├── schemas/           # Pydantic request/response schemas
│   ├── routes/            # auth, resumes, jobs, recommendations, career
│   ├── services/          # authentication, extraction, and analysis services
│   ├── agents/            # resume_analyzer.py; later job/career agents
│   ├── rag/               # (empty scaffold) → Member 4: loader.py, retriever.py, pipeline.py
│   └── utils/             # security.py, exceptions.py, deps.py, validators.py
├── knowledge_base/        # (empty scaffold) → Member 4: skills/, roadmaps/, jobs/, learning_resources/, resume_guidelines/
├── frontend/               # placeholder for frontend app → Member 5
├── data/                   # SQLite DB file lives here
├── uploads/                 # uploaded resume files
├── tests/                  # pytest suite
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

```bash
git clone <REPOSITORY_URL>
cd AI-Resume-Analyzer

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY etc.
# Set AI_API_KEY in .env to enable AI resume analysis (default: gemini-3.6-flash).

uvicorn app.main:app --reload
```

The API is now running at `http://127.0.0.1:8000`. Interactive docs at
`http://127.0.0.1:8000/docs`.

Tables are created automatically on startup (`init_db()` in `database.py`) —
no manual migration step is needed for this phase of the project.

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
| GET    | `/api/jobs/`          | No  | Stub — Member 3 |
| GET    | `/api/recommendations/{resume_id}` | Yes | Stub — Member 3 |
| GET    | `/api/career/`        | Yes | Stub — Member 4 |

Auth uses an `HttpOnly` session cookie (`session_id` by default), not a
bearer token — the browser sends it automatically on each request. When
calling the API from a frontend dev server, requests must be made with
credentials included (e.g. `fetch(url, { credentials: "include" })`) and the
frontend origin must be listed in `ALLOWED_ORIGINS`.

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

```bash
pytest tests/ -v
```

The test suite covers authentication plus resume validation, DOCX upload,
text extraction, analysis, and analysis retrieval. Resume analysis calls the
configured Gemini model and returns structured JSON; without `AI_API_KEY`, the
analysis endpoint returns `503` rather than producing a local fallback result.

## For the next team member

- Use `Depends(get_current_user)` from `app.utils.deps` to protect any new
  endpoint — see `app/routes/auth.py::me` for an example.
- Use `Depends(get_db)` from `app.database` to get a DB session.
- Resume files are stored under `uploads/` with generated names; user files
  are ignored by Git. PDF and DOCX uploads are limited to 10 MB.
- Raise `BadRequestError` / `NotFoundError` / etc. from `app.utils.exceptions`
  for consistent `{"detail": "..."}` error responses.
- `app/rag/` and `knowledge_base/` remain scaffolds for Member 4; Member 3
  can add job matching without changing the resume API prefixes.

## Git workflow

```bash
git checkout -b feature/backend-foundation
git add .
git commit -m "Implement backend foundation, database, and authentication"
git push origin feature/backend-foundation
```

Then open a Pull Request into `main`. After merge, the next team member
starts from the latest `main`:

```bash
git clone <REPOSITORY_URL>
cd AI-Resume-Analyzer
git checkout main
git pull origin main
```
