import dotenv
dotenv.load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import (
    health,
    repositories,
    search,
    symbols,
    relationships,
    ask
)
from utils.errors import CodebaseMentorError, LLMQuotaExhaustedError, RepositoryNotFoundError

app = FastAPI(
    title="AI Codebase Mentor API",
    description="Thin API layer for codebase investigation, search, symbol lookups, relationship tracing, and agent QA.",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(RepositoryNotFoundError)
def repository_not_found_handler(request: Request, exc: RepositoryNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.exception_handler(LLMQuotaExhaustedError)
def quota_exhausted_handler(request: Request, exc: LLMQuotaExhaustedError):
    return JSONResponse(
        status_code=429,
        content={"detail": str(exc)}
    )


@app.exception_handler(CodebaseMentorError)
def codebase_mentor_error_handler(request: Request, exc: CodebaseMentorError):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Backend Error: {str(exc)}"}
    )


# Include all sub-routers
app.include_router(health.router)
app.include_router(repositories.router)
app.include_router(search.router)
app.include_router(symbols.router)
app.include_router(relationships.router)
app.include_router(ask.router)
