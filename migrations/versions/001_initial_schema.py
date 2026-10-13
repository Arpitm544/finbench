"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('transaction_id', sa.String(length=64), nullable=False),
        sa.Column('step', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('name_orig', sa.String(length=64), nullable=False),
        sa.Column('oldbalance_org', sa.Float(), nullable=False),
        sa.Column('newbalance_orig', sa.Float(), nullable=False),
        sa.Column('name_dest', sa.String(length=64), nullable=False),
        sa.Column('oldbalance_dest', sa.Float(), nullable=False),
        sa.Column('newbalance_dest', sa.Float(), nullable=False),
        sa.Column('is_fraud', sa.Integer(), nullable=False),
        sa.Column('is_flagged_fraud', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dataset_version', sa.String(length=32), nullable=False, server_default='v1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_transactions_tx_id', 'transactions', ['transaction_id'], unique=True)
    op.create_index('idx_transactions_step', 'transactions', ['step'])
    op.create_index('idx_transactions_type', 'transactions', ['type'])
    op.create_index('idx_transactions_fraud', 'transactions', ['is_fraud'])
    op.create_index('idx_transactions_type_fraud', 'transactions', ['type', 'is_fraud'])
    op.create_index('idx_transactions_step_fraud', 'transactions', ['step', 'is_fraud'])
    op.create_index('idx_transactions_name_orig', 'transactions', ['name_orig'])
    op.create_index('idx_transactions_name_dest', 'transactions', ['name_dest'])
    op.create_index('idx_transactions_amount', 'transactions', ['amount'])

    # Data Quality Results
    op.create_table(
        'data_quality_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_id', sa.String(length=64), nullable=False),
        sa.Column('dataset_version', sa.String(length=32), nullable=False),
        sa.Column('total_records', sa.Integer(), nullable=False),
        sa.Column('missing_values_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('duplicate_records_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('negative_amounts_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('balance_inconsistencies_orig', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('balance_inconsistencies_dest', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('fraud_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('fraud_rate', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('status', sa.String(length=32), nullable=True, server_default='PASSED'),
        sa.Column('summary', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_dq_run_id', 'data_quality_results', ['run_id'])

    # Fraud Predictions
    op.create_table(
        'fraud_predictions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('model_name', sa.String(length=64), nullable=False),
        sa.Column('transaction_id', sa.String(length=64), nullable=False),
        sa.Column('fraud_probability', sa.Float(), nullable=False),
        sa.Column('predicted_label', sa.Integer(), nullable=False),
        sa.Column('actual_label', sa.Integer(), nullable=True),
        sa.Column('threshold_used', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )

    # Model Training Runs
    op.create_table(
        'model_training_runs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_id', sa.String(length=64), nullable=False),
        sa.Column('model_name', sa.String(length=64), nullable=False),
        sa.Column('hyperparameters', sa.JSON(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=False),
        sa.Column('recall', sa.Float(), nullable=False),
        sa.Column('f1_score', sa.Float(), nullable=False),
        sa.Column('pr_auc', sa.Float(), nullable=False),
        sa.Column('roc_auc', sa.Float(), nullable=False),
        sa.Column('expected_cost', sa.Float(), nullable=True),
        sa.Column('training_duration_seconds', sa.Float(), nullable=False),
        sa.Column('train_samples', sa.Integer(), nullable=False),
        sa.Column('test_samples', sa.Integer(), nullable=False),
        sa.Column('confusion_matrix', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_mtr_run_id', 'model_training_runs', ['run_id'], unique=True)

    # Benchmark Questions
    op.create_table(
        'benchmark_questions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('difficulty', sa.String(length=32), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('dataset_version', sa.String(length=32), nullable=False, server_default='v1'),
        sa.Column('reference_solution', sa.Text(), nullable=True),
        sa.Column('evaluation_method', sa.String(length=64), nullable=False),
        sa.Column('tolerance', sa.Float(), nullable=True, server_default='0.01'),
        sa.Column('freshness_category', sa.String(length=32), nullable=False, server_default='static'),
        sa.Column('rubric', sa.JSON(), nullable=True),
        sa.Column('assumptions', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending_verification'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_bq_category', 'benchmark_questions', ['category'])
    op.create_index('idx_bq_difficulty', 'benchmark_questions', ['difficulty'])

    # Benchmark Answers
    op.create_table(
        'benchmark_answers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question_id', sa.String(length=64), nullable=False),
        sa.Column('expected_answer', sa.JSON(), nullable=False),
        sa.Column('sql_result', sa.JSON(), nullable=True),
        sa.Column('python_result', sa.JSON(), nullable=True),
        sa.Column('discrepancy_delta', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('verification_status', sa.String(length=32), nullable=False, server_default='VERIFIED'),
        sa.Column('verified_by', sa.String(length=64), nullable=False, server_default='dual_ground_truth_engine'),
        sa.Column('verified_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['question_id'], ['benchmark_questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ba_question_id', 'benchmark_answers', ['question_id'], unique=True)

    # Evaluation Runs
    op.create_table(
        'evaluation_runs',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('model_name', sa.String(length=128), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('passed_questions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_questions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('accuracy_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('category_scores', sa.JSON(), nullable=True),
        sa.Column('difficulty_scores', sa.JSON(), nullable=True),
        sa.Column('average_latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_duration_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id')
    )

    # Evaluation Results
    op.create_table(
        'evaluation_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_id', sa.String(length=64), nullable=False),
        sa.Column('benchmark_id', sa.String(length=64), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('difficulty', sa.String(length=32), nullable=False),
        sa.Column('expected_answer', sa.JSON(), nullable=True),
        sa.Column('predicted_answer', sa.JSON(), nullable=True),
        sa.Column('score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['run_id'], ['evaluation_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_er_run_id', 'evaluation_results', ['run_id'])
    op.create_index('idx_er_benchmark_id', 'evaluation_results', ['benchmark_id'])


def downgrade() -> None:
    op.drop_table('evaluation_results')
    op.drop_table('evaluation_runs')
    op.drop_table('benchmark_answers')
    op.drop_table('benchmark_questions')
    op.drop_table('model_training_runs')
    op.drop_table('fraud_predictions')
    op.drop_table('data_quality_results')
    op.drop_table('transactions')
