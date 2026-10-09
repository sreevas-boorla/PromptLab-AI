import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import playground, optimizer, comparison, prompts, evaluations, analytics

# Auto-create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PromptLab AI API",
    description="Enterprise API for Prompt Engineering, Optimization, Model Comparison, and Real Evaluation",
    version="1.0.0"
)

# Phase 6: Configurable Production CORS Setup
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional access token for a private single-user backend.
@app.middleware("http")
async def protect_api(request: Request, call_next):
    import hmac
    if request.url.path.startswith("/api/v1/") and request.url.path != "/api/v1/health":
        token = os.getenv("PROMPTLAB_ACCESS_TOKEN", "")
        if os.getenv("PROMPTLAB_ENV", "development") == "production" and not token:
            return JSONResponse(status_code=503, content={"detail": "API access protection not configured"})
        if token and not hmac.compare_digest(request.headers.get("X-PromptLab-Token", ""), token):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)

# Global Exception Handlers for Provider & Validation Errors
@app.exception_handler(ValueError)
def handle_value_error(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": "ValidationError"}
    )

@app.exception_handler(RuntimeError)
def handle_runtime_error(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc), "error_type": "LLMProviderError"}
    )

# Include Routers
app.include_router(playground.router)
app.include_router(optimizer.router)
app.include_router(comparison.router)
app.include_router(prompts.router)
app.include_router(evaluations.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "PromptLab AI Engine API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
