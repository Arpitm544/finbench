from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class BenchmarkCategory(str, Enum):
    ADVANCED_SQL = "advanced_sql"
    FINANCIAL_STATISTICS = "financial_statistics"
    FRAUD_ANALYSIS = "fraud_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    BUSINESS_DECISIONS = "business_decisions"
    DATA_QUALITY = "data_quality"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"


class FreshnessCategory(str, Enum):
    STATIC = "static"
    SLOWLY_CHANGING = "slowly_changing"
    FREQUENTLY_CHANGING = "frequently_changing"
    LIVE_DEPENDENT = "live_dependent"


class EvaluationMethod(str, Enum):
    NUMERIC_TOLERANCE = "numeric_tolerance"
    SQL_EXECUTION = "sql_execution"
    STATISTICAL_VERIFICATION = "statistical_verification"
    RUBRIC_SCORING = "rubric_scoring"
    CONTRADICTORY_EVALUATION = "contradictory_evaluation"


class BenchmarkQuestionModel(BaseModel):
    id: str = Field(..., description="Unique benchmark ID, e.g. FIN-001")
    category: BenchmarkCategory
    difficulty: DifficultyLevel
    question: str
    dataset_version: str = "v1"
    expected_answer: Optional[Any] = None
    reference_solution: Optional[str] = None
    evaluation_method: EvaluationMethod
    tolerance: Optional[float] = 0.01
    freshness_category: FreshnessCategory = FreshnessCategory.STATIC
    rubric: Optional[Dict[str, Any]] = None
    assumptions: Optional[str] = None
    status: str = "pending_verification"


class RetiredQuestionEntry(BaseModel):
    question_id: str
    data_owner: str
    retirement_reason: str
    data_limitation: str
    replacement_question_id: str
    review_status: str = "retired"


class ContradictoryScenario(BaseModel):
    scenario_id: str
    description: str
    dataset_profile: str  # e.g. "Dataset A: High-loss corporate transfers" vs "Dataset B: Micro-transactions"
    loss_per_fraud: float
    cost_per_false_positive: float
    expected_recommendation: str  # "STRICTER_RULES" vs "RELAXED_RULES"
    rubric: Dict[str, Any]
