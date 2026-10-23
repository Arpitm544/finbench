from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from finbench.database import get_db, BenchmarkQuestion, BenchmarkAnswer

router = APIRouter(prefix="/benchmarks", tags=["AI Benchmarks"])


@router.get("")
def list_benchmarks(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    query = db.query(BenchmarkQuestion)
    if category:
        query = query.filter(BenchmarkQuestion.category == category)
    if difficulty:
        query = query.filter(BenchmarkQuestion.difficulty == difficulty)

    records = query.all()
    return [
        {
            "id": r.id,
            "category": r.category,
            "difficulty": r.difficulty,
            "question": r.question,
            "evaluation_method": r.evaluation_method,
            "freshness_category": r.freshness_category,
            "status": r.status,
            "tolerance": r.tolerance,
        }
        for r in records
    ]


@router.get("/{benchmark_id}")
def get_benchmark_detail(benchmark_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    bq = db.query(BenchmarkQuestion).filter(BenchmarkQuestion.id == benchmark_id).first()
    if not bq:
        raise HTTPException(status_code=404, detail=f"Benchmark question {benchmark_id} not found.")

    ba = db.query(BenchmarkAnswer).filter(BenchmarkAnswer.question_id == benchmark_id).first()

    return {
        "id": bq.id,
        "category": bq.category,
        "difficulty": bq.difficulty,
        "question": bq.question,
        "dataset_version": bq.dataset_version,
        "reference_solution": bq.reference_solution,
        "evaluation_method": bq.evaluation_method,
        "tolerance": bq.tolerance,
        "freshness_category": bq.freshness_category,
        "assumptions": bq.assumptions,
        "rubric": bq.rubric,
        "status": bq.status,
        "expected_answer": ba.expected_answer if ba else None,
        "verification_status": ba.verification_status if ba else "unverified",
    }
