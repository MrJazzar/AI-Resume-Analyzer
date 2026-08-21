"""
FastAPI application entrypoint: app instance, CORS, routers, startup
tasks, and global error handlers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routes import auth, career, jobs, recommendations, resumes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized. %s starting in %s mode.", settings.APP_NAME, settings.ENV)
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,  # required so the browser sends the session cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(recommendations.router)
app.include_router(career.router)


# ---------------------------------------------------------------------------
# Global error handlers — every error response has a consistent
# {"detail": "..."} shape, matching FastAPI's own HTTPException format.
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Invalid request data", "errors": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
