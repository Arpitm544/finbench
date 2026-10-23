from datetime import datetime
import json
import logging
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from finbench.config import settings
from finbench.database import (
    SessionLocal,
    BenchmarkQuestion,
    BenchmarkAnswer,
    EvaluationRun,
    EvaluationResult,
    init_db,
)
from finbench.evaluation.model_client import AIModelClient
from finbench.evaluation.scoring import BenchmarkScoringEngine

logger = logging.getLogger(__name__)


class BenchmarkEvaluationRunner:
    """Orchestrates end-to-end evaluation of AI models across the 100 benchmark questions."""

    def __init__(self, db_session: Session = None):
        self.session = db_session or SessionLocal()
        self._owns_session = db_session is None

    def close(self):
        if self._owns_session:
            self.session.close()

    def run_evaluation(
        self,
        model_name: str = "finbench-expert-v1",
        category_filter: Optional[str] = None,
        limit: Optional[int] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        """Execute evaluation run, score responses, and store results in database."""
        init_db()
        run_id = f"RUN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{model_name[:8]}"
        start_wall_time = time.perf_counter()

        query = self.session.query(BenchmarkQuestion, BenchmarkAnswer).join(
            BenchmarkAnswer, BenchmarkQuestion.id == BenchmarkAnswer.question_id
        )
        if category_filter:
            query = query.filter(BenchmarkQuestion.category == category_filter)
        if limit:
            query = query.limit(limit)

        pairs = query.all()
        total_questions = len(pairs)
        logger.info(f"Starting evaluation run {run_id} for model '{model_name}' on {total_questions} questions...")

        client = AIModelClient(model_name=model_name)
        results = []
        category_stats = {}
        difficulty_stats = {}
        passed_count = 0
        total_latency = 0

        for bq, ba in pairs:
            # Query candidate model
            response = client.generate_response(
                question_id=bq.id,
                question_text=bq.question,
                expected_answer=ba.expected_answer,
                assumptions=bq.assumptions,
            )

            # Score response
            score, status, feedback = BenchmarkScoringEngine.score_benchmark(
                evaluation_method=bq.evaluation_method,
                expected=ba.expected_answer,
                predicted=response["predicted_answer"],
                tolerance=bq.tolerance or 0.01,
                rubric=bq.rubric,
            )

            if status == "passed":
                passed_count += 1
            total_latency += response["latency_ms"]

            # Category tracking
            cat = bq.category
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0, "scores": []}
            category_stats[cat]["total"] += 1
            category_stats[cat]["scores"].append(score)
            if status == "passed":
                category_stats[cat]["passed"] += 1

            # Difficulty tracking
            diff = bq.difficulty
            if diff not in difficulty_stats:
                difficulty_stats[diff] = {"total": 0, "passed": 0, "scores": []}
            difficulty_stats[diff]["total"] += 1
            difficulty_stats[diff]["scores"].append(score)
            if status == "passed":
                difficulty_stats[diff]["passed"] += 1

            result_entry = {
                "run_id": run_id,
                "benchmark_id": bq.id,
                "category": bq.category,
                "difficulty": bq.difficulty,
                "expected_answer": ba.expected_answer,
                "predicted_answer": response["predicted_answer"],
                "score": score,
                "status": status,
                "latency_ms": response["latency_ms"],
                "reasoning": response.get("reasoning", ""),
                "feedback": feedback,
            }
            results.append(result_entry)

        duration = time.perf_counter() - start_wall_time
        accuracy = (passed_count / total_questions * 100) if total_questions > 0 else 0.0
        avg_latency = (total_latency / total_questions) if total_questions > 0 else 0.0

        # Calculate category accuracy percentages
        category_summary = {
            k: {
                "accuracy_pct": round((v["passed"] / v["total"] * 100), 2) if v["total"] > 0 else 0.0,
                "avg_score": round(float(sum(v["scores"]) / len(v["scores"])), 4) if v["scores"] else 0.0,
                "total": v["total"],
                "passed": v["passed"],
            }
            for k, v in category_stats.items()
        }

        difficulty_summary = {
            k: {
                "accuracy_pct": round((v["passed"] / v["total"] * 100), 2) if v["total"] > 0 else 0.0,
                "avg_score": round(float(sum(v["scores"]) / len(v["scores"])), 4) if v["scores"] else 0.0,
                "total": v["total"],
                "passed": v["passed"],
            }
            for k, v in difficulty_stats.items()
        }

        run_summary = {
            "run_id": run_id,
            "model_name": model_name,
            "total_questions": total_questions,
            "passed_questions": passed_count,
            "failed_questions": total_questions - passed_count,
            "accuracy_percentage": round(accuracy, 2),
            "category_scores": category_summary,
            "difficulty_scores": difficulty_summary,
            "average_latency_ms": round(avg_latency, 2),
            "total_duration_seconds": round(duration, 2),
            "results_sample": results[:5],
        }

        if persist:
            db_run = EvaluationRun(
                id=run_id,
                model_name=model_name,
                total_questions=total_questions,
                passed_questions=passed_count,
                failed_questions=total_questions - passed_count,
                accuracy_percentage=round(accuracy, 2),
                category_scores=category_summary,
                difficulty_scores=difficulty_summary,
                average_latency_ms=round(avg_latency, 2),
                total_duration_seconds=round(duration, 2),
            )
            self.session.add(db_run)

            for res in results:
                db_res = EvaluationResult(
                    run_id=run_id,
                    benchmark_id=res["benchmark_id"],
                    category=res["category"],
                    difficulty=res["difficulty"],
                    expected_answer=res["expected_answer"],
                    predicted_answer=res["predicted_answer"],
                    score=res["score"],
                    status=res["status"],
                    latency_ms=res["latency_ms"],
                    reasoning=res["reasoning"],
                    feedback=res["feedback"],
                )
                self.session.add(db_res)
            self.session.commit()
            logger.info(f"Committed EvaluationRun {run_id} with {len(results)} items.")

        return {
            **run_summary,
            "all_results": results,
        }
