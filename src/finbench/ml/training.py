from datetime import datetime
import logging
import time
from typing import Dict, Any, Tuple
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from finbench.config import settings
from finbench.database import SessionLocal, ModelTrainingRun, init_db
from finbench.ml.features import FeatureEngineeringPipeline

logger = logging.getLogger(__name__)


class FraudModelTrainer:
    """Trains and compares Logistic Regression, Random Forest, and LightGBM models."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}

    def prepare_datasets(
        self, df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        train_df, val_df, test_df = FeatureEngineeringPipeline.time_aware_split(df)

        X_train_raw = FeatureEngineeringPipeline.transform(train_df)
        X_val_raw = FeatureEngineeringPipeline.transform(val_df)
        X_test_raw = FeatureEngineeringPipeline.transform(test_df)

        # Scale continuous features
        X_train = self.scaler.fit_transform(X_train_raw)
        X_val = self.scaler.transform(X_val_raw)
        X_test = self.scaler.transform(X_test_raw)

        y_train = train_df["is_fraud"].values
        y_val = val_df["is_fraud"].values
        y_test = test_df["is_fraud"].values

        return X_train, y_train, X_val, y_val, X_test, y_test

    def train_logistic_regression(
        self, X_train: np.ndarray, y_train: np.ndarray
    ) -> Tuple[LogisticRegression, float]:
        start = time.perf_counter()
        clf = LogisticRegression(
            class_weight="balanced",
            max_iter=500,
            random_state=42,
            solver="lbfgs",
        )
        clf.fit(X_train, y_train)
        duration = time.perf_counter() - start
        self.models["logistic_regression"] = clf
        return clf, duration

    def train_random_forest(
        self, X_train: np.ndarray, y_train: np.ndarray
    ) -> Tuple[RandomForestClassifier, float]:
        start = time.perf_counter()
        clf = RandomForestClassifier(
            n_estimators=50,
            max_depth=12,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        clf.fit(X_train, y_train)
        duration = time.perf_counter() - start
        self.models["random_forest"] = clf
        return clf, duration

    def train_lightgbm(
        self, X_train: np.ndarray, y_train: np.ndarray
    ) -> Tuple[lgb.LGBMClassifier, float]:
        start = time.perf_counter()
        # Scale pos weight to balance rare positive class
        neg_count = np.sum(y_train == 0)
        pos_count = max(1, np.sum(y_train == 1))
        scale_pos_weight = neg_count / pos_count

        clf = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.05,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            verbose=-1,
        )
        clf.fit(X_train, y_train)
        duration = time.perf_counter() - start
        self.models["lightgbm"] = clf
        return clf, duration
