import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd

from finbench.ml.features import FeatureEngineeringPipeline

logger = logging.getLogger(__name__)


class FraudInferenceEngine:
    """Production scoring interface for real-time transaction inference."""

    def __init__(self, model, scaler=None, default_threshold: float = 0.5):
        self.model = model
        self.scaler = scaler
        self.default_threshold = default_threshold

    def score_transactions(self, df: pd.DataFrame, threshold: float = None) -> pd.DataFrame:
        th = threshold if threshold is not None else self.default_threshold
        features_df = FeatureEngineeringPipeline.transform(df)

        if self.scaler is not None:
            X = self.scaler.transform(features_df)
        else:
            X = features_df.values

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(X)[:, 1]
        else:
            probabilities = self.model.decision_function(X)

        df_out = df.copy()
        df_out["fraud_probability"] = np.round(probabilities, 4)
        df_out["predicted_fraud"] = (probabilities >= th).astype(int)
        return df_out
