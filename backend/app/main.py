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

# Single-user authentication. Secret never reaches frontend code or browser storage.
import hashlib
import hmac
import time
from fastapi import Body, Response

def sign_session(expiry: str, secret: str) -> str:
    return hmac.new(secret.encode(), expiry.encode(), hashlib.sha256).hexdigest()

@app.post("/api/v1/auth/login")
def login(response: Response, data: dict = Body(...)):
    secret = os.getenv("PROMPTLAB_ACCESS_TOKEN", "")
    supplied = data.get("password", "")
    if not secret or not isinstance(supplied, str) or not hmac.compare_digest(secret, supplied):
        return JSONResponse(status_code=401, content={"detail": "Invalid passphrase"})
    expiry = str(int(time.time()) + 8 * 3600)
    response.set_cookie("promptlab_session", expiry + "." + sign_session(expiry, secret),
                        httponly=True, secure=os.getenv("PROMPTLAB_ENV") == "production",
                        samesite="lax", max_age=28800, path="/api/v1")
    return {"authenticated": True}

@app.post("/api/v1/auth/logout")
def logout(response: Response):
    response.delete_cookie("promptlab_session", path="/api/v1")
    return {"authenticated": False}

@app.middleware("http")
async def protect_api(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/v1/") and path not in ("/api/v1/health", "/api/v1/auth/login"):
        secret = os.getenv("PROMPTLAB_ACCESS_TOKEN", "")
        if os.getenv("PROMPTLAB_ENV", "development") == "production" and not secret:
            return JSONResponse(status_code=503, content={"detail": "Production access not configured"})
        if secret:
            try:
                expiry, signature = request.cookies.get("promptlab_session", "").split(".", 1)
                valid = int(expiry) > int(time.time()) and hmac.compare_digest(signature, sign_session(expiry, secret))
            except (ValueError, TypeError):
                valid = False
            if not valid:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                origin = request.headers.get("origin")
                if origin and origin not in origins:
                    return JSONResponse(status_code=403, content={"detail": "Untrusted origin"})
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
