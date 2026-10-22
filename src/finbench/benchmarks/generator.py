import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from finbench.config import settings
from finbench.database import SessionLocal, BenchmarkQuestion, init_db
from finbench.benchmarks.schemas import BenchmarkQuestionModel, RetiredQuestionEntry
from finbench.benchmarks.templates import BENCHMARK_CATALOG

logger = logging.getLogger(__name__)


def generate_retired_question_registry() -> List[Dict[str, Any]]:
    """Feature A: Structured registry of questions retired due to domain/data evolution."""
    return [
        {
            "question_id": "RET-001",
            "data_owner": "Chief Risk Officer / Fraud Operations",
            "retirement_reason": "Naive single-threshold filters ($200k) ceased providing actionable risk separation.",
            "data_limitation": "Attackers structured transfers to $199,999 to evade static threshold flags.",
            "replacement_question_id": "FIN-009",
            "review_status": "retired",
        },
        {
            "question_id": "RET-002",
            "data_owner": "VP of Payment Gateway Infrastructure",
            "retirement_reason": "Overall network average transaction size masked extreme multimodal channel divergence.",
            "data_limitation": "Aggregating merchant payments with institutional transfers distorted risk baselines.",
            "replacement_question_id": "FIN-002",
            "review_status": "retired",
        },
        {
            "question_id": "RET-003",
            "data_owner": "Head of Financial Crime Compliance",
            "retirement_reason": "Origin account zeroing alone triggered excessive false alerts on low-balance retail users.",
            "data_limitation": "Retail users routinely spend their entire paycheck down to $0 for living expenses.",
            "replacement_question_id": "FIN-007",
            "review_status": "retired",
        },
        {
            "question_id": "RET-004",
            "data_owner": "Lead Data Scientist (AML Analytics)",
            "retirement_reason": "Standard Pearson linear correlation failed to capture nonlinear log-normal money distributions.",
            "data_limitation": "Extreme outliers produced spurious correlation coefficients.",
            "replacement_question_id": "FIN-035",
            "review_status": "retired",
        },
        {
            "question_id": "RET-005",
            "data_owner": "Director of Customer Trust & Safety",
            "retirement_reason": "Static fraud prevention targets caused unacceptable customer checkout drop-off during seasonal peaks.",
            "data_limitation": "Static thresholds did not account for varying false positive customer churn costs.",
            "replacement_question_id": "FIN-076",
            "review_status": "retired",
        },
    ]


def generate_data_owner_interview_questionnaire() -> Dict[str, Any]:
    """Feature A: Interview Questionnaire for domain experts regarding analytical question lifecycle."""
    return {
        "title": "FinBench Data Owner Question Lifecycle & Retirement Questionnaire",
        "purpose": "Identify obsolete heuristics, blind spots, and evolving regulatory standards across financial risk operations.",
        "interviewee_roles": [
            "Chief Risk Officer (CRO)",
            "Head of Anti-Money Laundering (AML)",
            "Director of Payment Gateway Risk",
            "Principal Fraud Data Scientist",
        ],
        "questions": [
            {
                "id": "Q1",
                "question": "Which analytical questions or legacy rules that your team relied upon 12 months ago have been formally abandoned or deprioritized, and what specific adversary behavior caused their retirement?",
                "objective": "Uncover how attackers adapt to static detection filters (e.g. smurfing below $200k thresholds).",
            },
            {
                "id": "Q2",
                "question": "What critical data fields or contextual telemetry were missing in your legacy transaction schemas that made answering key risk questions impossible?",
                "objective": "Document schema limitations and justify additions like device fingerprinting or ledger discrepancy indicators.",
            },
            {
                "id": "Q3",
                "question": "How do you quantify the business cost of false positives (customer friction, cart abandonment, support tickets) versus unrecovered fraud losses when establishing alert thresholds?",
                "objective": "Validate the economic objective function for contradictory advice evaluation.",
            },
            {
                "id": "Q4",
                "question": "Under what circumstances do you intentionally accept higher residual fraud rates to achieve strategic corporate growth targets?",
                "objective": "Assess how leadership balances security with conversion rate frontiers.",
            },
        ],
    }


def generate_benchmark_suite(
    output_path: Path = None,
    persist_db: bool = True,
) -> List[Dict[str, Any]]:
    """Validate, enrich, and serialize the 100-question FinBench benchmark suite."""
    target_path = output_path or (settings.DATA_PROCESSED_DIR / "benchmark_questions_100.json")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating full {len(BENCHMARK_CATALOG)} benchmark questions...")
    validated_questions = []

    for item in BENCHMARK_CATALOG:
        q_obj = BenchmarkQuestionModel(**item)
        validated_questions.append(q_obj.model_dump())

    # Write JSON artifact
    with open(target_path, "w") as f:
        json.dump(validated_questions, f, indent=2)
    logger.info(f"Saved {len(validated_questions)} benchmark questions to {target_path}")

    # Persist to database
    if persist_db:
        init_db()
        with SessionLocal() as session:
            for item in validated_questions:
                existing = session.query(BenchmarkQuestion).filter_by(id=item["id"]).first()
                if not existing:
                    bq = BenchmarkQuestion(
                        id=item["id"],
                        category=item["category"],
                        difficulty=item["difficulty"],
                        question=item["question"],
                        dataset_version=item["dataset_version"],
                        reference_solution=item["reference_solution"],
                        evaluation_method=item["evaluation_method"],
                        tolerance=item["tolerance"],
                        freshness_category=item["freshness_category"],
                        rubric=item["rubric"],
                        assumptions=item["assumptions"],
                        status="pending_verification",
                    )
                    session.add(bq)
            session.commit()
            logger.info("Persisted all benchmark questions to database.")

    return validated_questions


if __name__ == "__main__":
    generate_benchmark_suite()
