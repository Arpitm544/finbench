import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from finbench.config import settings
from finbench.database import SessionLocal, Transaction

logger = logging.getLogger(__name__)


class FinancialRiskAnalytics:
    """Computes rule-based and behavioral risk segmentation on transactions."""

    def __init__(self, db_session: Session = None):
        self.session = db_session or SessionLocal()
        self._owns_session = db_session is None

    def close(self):
        if self._owns_session:
            self.session.close()

    def calculate_risk_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Module C: Rule-based composite risk score [0 to 100] based on red flags.
        
        Red flag weights:
        - Transfer or Cashout channel: +25
        - Account drained to zero (orig balance error): +30
        - Destination remaining at zero after deposit: +20
        - High amount (> P95): +15
        - Nocturnal hours (step % 24 in [0..5]): +10
        """
        scores = np.zeros(len(df))

        # Channel risk
        is_transfer_or_cashout = df["type"].isin(["TRANSFER", "CASH_OUT"])
        scores += np.where(is_transfer_or_cashout, 25, 0)

        # Origin account emptied
        drained_orig = (df["oldbalance_org"] > 0) & (df["newbalance_orig"] == 0)
        scores += np.where(drained_orig, 30, 0)

        # Dest account remains zero
        zero_dest = (df["newbalance_dest"] == 0) & is_transfer_or_cashout
        scores += np.where(zero_dest, 20, 0)

        # High amount (> 200,000)
        high_amt = df["amount"] > 200000
        scores += np.where(high_amt, 15, 0)

        # Nocturnal
        nocturnal = (df["step"] % 24).isin([0, 1, 2, 3, 4, 5])
        scores += np.where(nocturnal, 10, 0)

        df["risk_score"] = np.clip(scores, 0, 100)
        df["risk_tier"] = pd.cut(
            df["risk_score"],
            bins=[-1, 25, 55, 75, 100],
            labels=["Low", "Medium", "High", "Critical"],
        )
        return df

    def evaluate_cost_benefit_curve(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        cost_false_positive: float = 25.0,  # Manual review or customer friction cost
        cost_false_negative_avg: float = 12000.0,  # Average financial loss from missed fraud
    ) -> Dict[str, Any]:
        """Module F: Business Decision Analytics evaluating operational cost curve across thresholds."""
        thresholds = np.linspace(0.01, 0.99, 99)
        best_threshold = 0.5
        min_cost = float("inf")
        tradeoff_curve = []

        total_fraud = np.sum(y_true == 1)
        total_legit = np.sum(y_true == 0)

        for th in thresholds:
            y_pred = (y_prob >= th).astype(int)
            fp = np.sum((y_pred == 1) & (y_true == 0))
            fn = np.sum((y_pred == 0) & (y_true == 1))
            tp = np.sum((y_pred == 1) & (y_true == 1))

            cost = (fp * cost_false_positive) + (fn * cost_false_negative_avg)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

            if cost < min_cost:
                min_cost = cost
                best_threshold = float(th)

            tradeoff_curve.append({
                "threshold": round(float(th), 2),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "true_positives": int(tp),
                "precision": round(float(precision), 4),
                "recall": round(float(recall), 4),
                "total_expected_cost": round(float(cost), 2),
            })

        return {
            "optimal_threshold": round(best_threshold, 2),
            "minimum_expected_cost": round(min_cost, 2),
            "cost_assumptions": {
                "cost_per_false_positive": cost_false_positive,
                "cost_per_false_negative": cost_false_negative_avg,
            },
            "tradeoff_curve": tradeoff_curve[::10],  # Subsample for reporting
        }
