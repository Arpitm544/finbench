-- FinBench PostgreSQL Schema Definition
-- Core tables for Financial Risk Analytics & AI Benchmark Evaluation System

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(64) UNIQUE NOT NULL,
    step INTEGER NOT NULL,
    type VARCHAR(32) NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    name_orig VARCHAR(64) NOT NULL,
    oldbalance_org DOUBLE PRECISION NOT NULL,
    newbalance_orig DOUBLE PRECISION NOT NULL,
    name_dest VARCHAR(64) NOT NULL,
    oldbalance_dest DOUBLE PRECISION NOT NULL,
    newbalance_dest DOUBLE PRECISION NOT NULL,
    is_fraud INTEGER NOT NULL DEFAULT 0,
    is_flagged_fraud INTEGER NOT NULL DEFAULT 0,
    dataset_version VARCHAR(32) NOT NULL DEFAULT 'v1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Optimization indexes for high-frequency queries
CREATE INDEX IF NOT EXISTS idx_transactions_step ON transactions(step);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_fraud ON transactions(is_fraud);
CREATE INDEX IF NOT EXISTS idx_transactions_type_fraud ON transactions(type, is_fraud);
CREATE INDEX IF NOT EXISTS idx_transactions_step_fraud ON transactions(step, is_fraud);
CREATE INDEX IF NOT EXISTS idx_transactions_name_orig ON transactions(name_orig);
CREATE INDEX IF NOT EXISTS idx_transactions_name_dest ON transactions(name_dest);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);

CREATE TABLE IF NOT EXISTS data_quality_results (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    dataset_version VARCHAR(32) NOT NULL DEFAULT 'v1',
    total_records INTEGER NOT NULL,
    missing_values_count INTEGER DEFAULT 0,
    duplicate_records_count INTEGER DEFAULT 0,
    negative_amounts_count INTEGER DEFAULT 0,
    balance_inconsistencies_orig INTEGER DEFAULT 0,
    balance_inconsistencies_dest INTEGER DEFAULT 0,
    fraud_count INTEGER DEFAULT 0,
    fraud_rate DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(32) DEFAULT 'PASSED',
    summary JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS fraud_predictions (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(64) NOT NULL,
    transaction_id VARCHAR(64) NOT NULL,
    fraud_probability DOUBLE PRECISION NOT NULL,
    predicted_label INTEGER NOT NULL,
    actual_label INTEGER,
    threshold_used DOUBLE PRECISION DEFAULT 0.5 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS model_training_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(64) UNIQUE NOT NULL,
    model_name VARCHAR(64) NOT NULL,
    hyperparameters JSONB,
    precision DOUBLE PRECISION NOT NULL,
    recall DOUBLE PRECISION NOT NULL,
    f1_score DOUBLE PRECISION NOT NULL,
    pr_auc DOUBLE PRECISION NOT NULL,
    roc_auc DOUBLE PRECISION NOT NULL,
    expected_cost DOUBLE PRECISION,
    training_duration_seconds DOUBLE PRECISION NOT NULL,
    train_samples INTEGER NOT NULL,
    test_samples INTEGER NOT NULL,
    confusion_matrix JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS benchmark_questions (
    id VARCHAR(64) PRIMARY KEY,
    category VARCHAR(64) NOT NULL,
    difficulty VARCHAR(32) NOT NULL,
    question TEXT NOT NULL,
    dataset_version VARCHAR(32) NOT NULL DEFAULT 'v1',
    reference_solution TEXT,
    evaluation_method VARCHAR(64) NOT NULL,
    tolerance DOUBLE PRECISION DEFAULT 0.01,
    freshness_category VARCHAR(32) NOT NULL DEFAULT 'static',
    rubric JSONB,
    assumptions TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'pending_verification',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS benchmark_answers (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(64) UNIQUE NOT NULL REFERENCES benchmark_questions(id) ON DELETE CASCADE,
    expected_answer JSONB NOT NULL,
    sql_result JSONB,
    python_result JSONB,
    discrepancy_delta DOUBLE PRECISION DEFAULT 0.0,
    verification_status VARCHAR(32) NOT NULL DEFAULT 'VERIFIED',
    verified_by VARCHAR(64) NOT NULL DEFAULT 'dual_ground_truth_engine',
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluation_runs (
    id VARCHAR(64) PRIMARY KEY,
    model_name VARCHAR(128) NOT NULL,
    total_questions INTEGER NOT NULL DEFAULT 0,
    passed_questions INTEGER NOT NULL DEFAULT 0,
    failed_questions INTEGER NOT NULL DEFAULT 0,
    accuracy_percentage DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    category_scores JSONB,
    difficulty_scores JSONB,
    average_latency_ms DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    total_duration_seconds DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluation_results (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL REFERENCES evaluation_runs(id) ON DELETE CASCADE,
    benchmark_id VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    difficulty VARCHAR(32) NOT NULL,
    expected_answer JSONB,
    predicted_answer JSONB,
    score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    status VARCHAR(32) NOT NULL,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    reasoning TEXT,
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
