from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from finbench.config import settings
from finbench.database import init_db
from finbench.api.routes import analytics, fraud, benchmarks, evaluations

app = FastAPI(
    title="FinBench API",
    description="Financial Risk Analytics & AI Benchmark Evaluation REST API",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api")
app.include_router(fraud.router, prefix="/api")
app.include_router(benchmarks.router, prefix="/api")
app.include_router(evaluations.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "FinBench API",
        "environment": settings.ENVIRONMENT,
        "database": settings.DATABASE_URL.split("://")[0],
        "version": "0.1.0",
    }


@app.get("/api/reports/summary", tags=["Reports"])
def get_reports_summary() -> Dict[str, Any]:
    return {
        "dataset_records": 10000,
        "verified_benchmarks": 100,
        "models_evaluated": 3,
        "top_performing_model": "finbench-expert-v1",
        "best_accuracy_pct": 94.0,
        "data_quality_status": "PASSED",
    }
