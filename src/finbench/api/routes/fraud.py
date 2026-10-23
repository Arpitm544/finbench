from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from finbench.database import get_db, ModelTrainingRun

router = APIRouter(prefix="/models", tags=["Machine Learning"])


@router.get("")
def list_trained_models(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    runs = db.query(ModelTrainingRun).order_by(ModelTrainingRun.created_at.desc()).all()
    return [
        {
            "run_id": r.run_id,
            "model_name": r.model_name,
            "precision": r.precision,
            "recall": r.recall,
            "f1_score": r.f1_score,
            "pr_auc": r.pr_auc,
            "roc_auc": r.roc_auc,
            "expected_cost": r.expected_cost,
            "training_duration_seconds": r.training_duration_seconds,
            "train_samples": r.train_samples,
            "test_samples": r.test_samples,
            "confusion_matrix": r.confusion_matrix,
        }
        for r in runs
    ]
