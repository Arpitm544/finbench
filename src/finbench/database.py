from collections.abc import Generator
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

from finbench.config import settings

# Engine configuration (supporting SQLite and PostgreSQL transparently)
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True if not settings.DATABASE_URL.startswith("sqlite") else False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transaction(Base):
    """Financial transaction records matching PaySim schema with persistent transaction ID."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(64), unique=True, index=True, nullable=False)
    step = Column(Integer, index=True, nullable=False)
    type = Column(String(32), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    name_orig = Column(String(64), index=True, nullable=False)
    oldbalance_org = Column(Float, nullable=False)
    newbalance_orig = Column(Float, nullable=False)
    name_dest = Column(String(64), index=True, nullable=False)
    oldbalance_dest = Column(Float, nullable=False)
    newbalance_dest = Column(Float, nullable=False)
    is_fraud = Column(Integer, index=True, nullable=False)
    is_flagged_fraud = Column(Integer, default=0, nullable=False)
    dataset_version = Column(String(32), default="v1", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_transactions_type_fraud", "type", "is_fraud"),
        Index("idx_transactions_step_fraud", "step", "is_fraud"),
        Index("idx_transactions_amount", "amount"),
    )


class DataQualityResult(Base):
    """Data validation and consistency checks results."""
    __tablename__ = "data_quality_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), index=True, nullable=False)
    dataset_version = Column(String(32), default="v1", nullable=False)
    total_records = Column(Integer, nullable=False)
    missing_values_count = Column(Integer, default=0)
    duplicate_records_count = Column(Integer, default=0)
    negative_amounts_count = Column(Integer, default=0)
    balance_inconsistencies_orig = Column(Integer, default=0)
    balance_inconsistencies_dest = Column(Integer, default=0)
    fraud_count = Column(Integer, default=0)
    fraud_rate = Column(Float, default=0.0)
    status = Column(String(32), default="PASSED")
    summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FraudPrediction(Base):
    """Machine learning fraud score predictions."""
    __tablename__ = "fraud_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(64), index=True, nullable=False)
    transaction_id = Column(String(64), index=True, nullable=False)
    fraud_probability = Column(Float, nullable=False)
    predicted_label = Column(Integer, nullable=False)
    actual_label = Column(Integer, nullable=True)
    threshold_used = Column(Float, default=0.5, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ModelTrainingRun(Base):
    """ML training runs metadata and validation metrics."""
    __tablename__ = "model_training_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    model_name = Column(String(64), nullable=False)
    hyperparameters = Column(JSON, nullable=True)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    pr_auc = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=False)
    expected_cost = Column(Float, nullable=True)
    training_duration_seconds = Column(Float, nullable=False)
    train_samples = Column(Integer, nullable=False)
    test_samples = Column(Integer, nullable=False)
    confusion_matrix = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class BenchmarkQuestion(Base):
    """AI benchmark analytical questions."""
    __tablename__ = "benchmark_questions"

    id = Column(String(64), primary_key=True)  # e.g., FIN-001
    category = Column(String(64), index=True, nullable=False)  # advanced_sql, fraud_analysis, etc.
    difficulty = Column(String(32), index=True, nullable=False)  # easy, medium, hard, expert
    question = Column(Text, nullable=False)
    dataset_version = Column(String(32), default="v1", nullable=False)
    reference_solution = Column(Text, nullable=True)  # File path or query
    evaluation_method = Column(String(64), nullable=False)  # numeric_tolerance, sql_execution, rubric
    tolerance = Column(Float, default=0.01, nullable=True)
    freshness_category = Column(String(32), default="static", nullable=False)
    rubric = Column(JSON, nullable=True)
    assumptions = Column(Text, nullable=True)
    status = Column(String(32), default="pending_verification", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    answer = relationship("BenchmarkAnswer", back_populates="question_rel", uselist=False)


class BenchmarkAnswer(Base):
    """Verified ground-truth reference answers."""
    __tablename__ = "benchmark_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(64), ForeignKey("benchmark_questions.id"), unique=True, index=True, nullable=False)
    expected_answer = Column(JSON, nullable=False)  # Can be float, dict, string, or list
    sql_result = Column(JSON, nullable=True)
    python_result = Column(JSON, nullable=True)
    discrepancy_delta = Column(Float, default=0.0)
    verification_status = Column(String(32), default="VERIFIED", nullable=False)
    verified_by = Column(String(64), default="dual_ground_truth_engine", nullable=False)
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    question_rel = relationship("BenchmarkQuestion", back_populates="answer")


class EvaluationRun(Base):
    """AI model benchmark evaluation sessions."""
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True)  # e.g., RUN-001
    model_name = Column(String(128), index=True, nullable=False)
    total_questions = Column(Integer, default=0, nullable=False)
    passed_questions = Column(Integer, default=0, nullable=False)
    failed_questions = Column(Integer, default=0, nullable=False)
    accuracy_percentage = Column(Float, default=0.0, nullable=False)
    category_scores = Column(JSON, nullable=True)
    difficulty_scores = Column(JSON, nullable=True)
    average_latency_ms = Column(Float, default=0.0, nullable=False)
    total_duration_seconds = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    results = relationship("EvaluationResult", back_populates="run_rel")


class EvaluationResult(Base):
    """Individual benchmark question evaluation scores and predictions."""
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), ForeignKey("evaluation_runs.id"), index=True, nullable=False)
    benchmark_id = Column(String(64), index=True, nullable=False)
    category = Column(String(64), nullable=False)
    difficulty = Column(String(32), nullable=False)
    expected_answer = Column(JSON, nullable=True)
    predicted_answer = Column(JSON, nullable=True)
    score = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    status = Column(String(32), nullable=False)  # passed, failed, error
    latency_ms = Column(Integer, default=0, nullable=False)
    reasoning = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    run_rel = relationship("EvaluationRun", back_populates="results")


def get_db() -> Generator[Session, None, None]:
    """Dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
