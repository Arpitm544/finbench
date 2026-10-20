import logging
from typing import Tuple, List
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "amount_log",
    "oldbalance_org_log",
    "oldbalance_dest_log",
    "error_balance_orig",
    "error_balance_dest",
    "orig_depleted_ratio",
    "is_zero_dest_balance",
    "hour_sin",
    "hour_cos",
    "type_CASH_OUT",
    "type_TRANSFER",
    "type_PAYMENT",
    "type_CASH_IN",
    "type_DEBIT",
    "is_high_amount",
]


class FeatureEngineeringPipeline:
    """Extracts leakage-free temporal and financial accounting features from transaction data."""

    @classmethod
    def transform(cls, df: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame(index=df.index)

        # 1. Log transformations for heavy tails (adding 1 to prevent log(0))
        features["amount_log"] = np.log1p(df["amount"])
        features["oldbalance_org_log"] = np.log1p(df["oldbalance_org"])
        features["oldbalance_dest_log"] = np.log1p(df["oldbalance_dest"])

        # 2. Accounting ledger discrepancies (domain invariants)
        # Difference between expected post-balance and reported balance
        features["error_balance_orig"] = df["newbalance_orig"] + df["amount"] - df["oldbalance_org"]
        features["error_balance_dest"] = df["oldbalance_dest"] + df["amount"] - df["newbalance_dest"]

        # 3. Behavioral ratios
        features["orig_depleted_ratio"] = df["amount"] / (df["oldbalance_org"] + 1.0)
        features["is_zero_dest_balance"] = (df["newbalance_dest"] == 0).astype(int)

        # 4. Cyclic 24-hour time step encoding (sin/cos encoding of hour of day)
        hour = df["step"] % 24
        features["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
        features["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)

        # 5. One-hot encoding of transaction types
        for t in ["CASH_OUT", "TRANSFER", "PAYMENT", "CASH_IN", "DEBIT"]:
            col_name = f"type_{t}"
            features[col_name] = (df["type"] == t).astype(int)

        # 6. High-amount heuristic
        features["is_high_amount"] = (df["amount"] > 200000).astype(int)

        return features[FEATURE_COLUMNS]

    @classmethod
    def time_aware_split(
        cls, df: pd.DataFrame, train_ratio: float = 0.70, val_ratio: float = 0.15
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Perform strict chronological time-aware split based on simulation step to prevent future data leakage."""
        sorted_steps = np.sort(df["step"].unique())
        n_steps = len(sorted_steps)

        train_cutoff_step = sorted_steps[int(n_steps * train_ratio)]
        val_cutoff_step = sorted_steps[int(n_steps * (train_ratio + val_ratio))]

        train_df = df[df["step"] <= train_cutoff_step].copy()
        val_df = df[(df["step"] > train_cutoff_step) & (df["step"] <= val_cutoff_step)].copy()
        test_df = df[df["step"] > val_cutoff_step].copy()

        logger.info(
            f"Time-aware split: Train (step <= {train_cutoff_step}) = {len(train_df):,} rows | "
            f"Val ({train_cutoff_step} < step <= {val_cutoff_step}) = {len(val_df):,} rows | "
            f"Test (step > {val_cutoff_step}) = {len(test_df):,} rows"
        )
        return train_df, val_df, test_df
