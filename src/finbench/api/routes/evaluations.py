from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from finbench.database import get_db, EvaluationRun, EvaluationResult
from finbench.evaluation.runner import BenchmarkEvaluationRunner

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


class EvaluationRequest(BaseModel):
    model_name: str = "finbench-expert-v1"
    category: Optional[str] = None
    limit: Optional[int] = None


@router.post("")
def start_evaluation(payload: EvaluationRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    runner = BenchmarkEvaluationRunner(db)
    res = runner.run_evaluation(
        model_name=payload.model_name,
        category_filter=payload.category,
        limit=payload.limit,
        persist=True,
    )
    return {
        "run_id": res["run_id"],
        "model_name": res["model_name"],
        "total_questions": res["total_questions"],
        "passed_questions": res["passed_questions"],
        "accuracy_percentage": res["accuracy_percentage"],
        "average_latency_ms": res["average_latency_ms"],
        "total_duration_seconds": res["total_duration_seconds"],
        "category_scores": res["category_scores"],
    }


@router.get("/{run_id}")
def get_evaluation_status(run_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    run = db.query(EvaluationRun).filter(EvaluationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Evaluation run {run_id} not found.")

    return {
        "run_id": run.id,
        "model_name": run.model_name,
        "total_questions": run.total_questions,
        "passed_questions": run.passed_questions,
        "failed_questions": run.failed_questions,
        "accuracy_percentage": run.accuracy_percentage,
        "average_latency_ms": run.average_latency_ms,
        "total_duration_seconds": run.total_duration_seconds,
        "category_scores": run.category_scores,
        "difficulty_scores": run.difficulty_scores,
        "created_at": run.created_at.isoformat(),
    }


@router.get("/{run_id}/results")
def get_evaluation_results(run_id: str, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    results = db.query(EvaluationResult).filter(EvaluationResult.run_id == run_id).all()
    if not results:
        raise HTTPException(status_code=404, detail=f"No results found for run {run_id}.")

    return [
        {
            "benchmark_id": r.benchmark_id,
            "category": r.category,
            "difficulty": r.difficulty,
            "score": r.score,
            "status": r.status,
            "latency_ms": r.latency_ms,
            "expected_answer": r.expected_answer,
            "predicted_answer": r.predicted_answer,
            "feedback": r.feedback,
        }
        for r in results
    ]
