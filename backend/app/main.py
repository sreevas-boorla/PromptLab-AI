from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import playground, optimizer, comparison, prompts, evaluations, analytics

# Auto-create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PromptLab AI API",
    description="Enterprise API for Prompt Engineering, Optimization, Model Comparison, and Evaluation",
    version="1.0.0"
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
