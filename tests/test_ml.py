import numpy as np
from finbench.ml.features import FeatureEngineeringPipeline
from finbench.ml.training import FraudModelTrainer
from finbench.ml.evaluation import ModelEvaluator


def test_feature_engineering_pipeline(sample_df):
    features = FeatureEngineeringPipeline.transform(sample_df)
    assert len(features) == len(sample_df)
    assert "amount_log" in features.columns
    assert "error_balance_orig" in features.columns
    assert "hour_sin" in features.columns
    assert "hour_cos" in features.columns
    assert "is_zero_dest_balance" in features.columns
    # Check no NaN values created
    assert features.isnull().sum().sum() == 0


def test_time_aware_split(sample_df):
    train_df, val_df, test_df = FeatureEngineeringPipeline.time_aware_split(sample_df)
    assert len(train_df) > 0
    assert len(val_df) > 0
    assert len(test_df) > 0
    # Strict temporal ordering: max train step <= min val step
    assert train_df["step"].max() <= val_df["step"].min()
    assert val_df["step"].max() <= test_df["step"].min()


def test_evaluator_metrics():
    y_true = np.array([0, 0, 0, 0, 1, 1, 0, 1, 0, 0])
    y_prob = np.array([0.1, 0.2, 0.05, 0.3, 0.9, 0.85, 0.4, 0.75, 0.1, 0.2])

    metrics = ModelEvaluator.evaluate_predictions(y_true, y_prob, threshold=0.5)
    assert "precision" in metrics
    assert "recall" in metrics
    assert "pr_auc" in metrics
    assert "expected_cost" in metrics
    assert metrics["precision"] > 0.0
    assert metrics["recall"] > 0.0
