from dataclasses import dataclass
from typing import Dict, Any, List
import pandas as pd
import numpy as np


@dataclass
class ValidationRuleResult:
    rule_name: str
    passed: bool
    failing_records_count: int
    failing_percentage: float
    description: str


class FinancialDataQualityChecker:
    """Executes deterministic audit checks on transaction data frames."""

    VALID_TYPES = {"PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"}

    @classmethod
    def check_missing_values(cls, df: pd.DataFrame) -> ValidationRuleResult:
        null_counts = df.isnull().sum().sum()
        total_cells = df.size
        pct = (null_counts / total_cells * 100) if total_cells > 0 else 0.0
        return ValidationRuleResult(
            rule_name="missing_values_check",
            passed=(null_counts == 0),
            failing_records_count=int(null_counts),
            failing_percentage=round(pct, 4),
            description="All transaction columns must contain non-null values.",
        )

    @classmethod
    def check_negative_amounts(cls, df: pd.DataFrame) -> ValidationRuleResult:
        negative_count = (df["amount"] < 0).sum()
        pct = (negative_count / len(df) * 100) if len(df) > 0 else 0.0
        return ValidationRuleResult(
            rule_name="negative_amounts_check",
            passed=(negative_count == 0),
            failing_records_count=int(negative_count),
            failing_percentage=round(pct, 4),
            description="Transaction amounts must be non-negative.",
        )

    @classmethod
    def check_invalid_types(cls, df: pd.DataFrame) -> ValidationRuleResult:
        invalid_types = ~df["type"].isin(cls.VALID_TYPES)
        count = invalid_types.sum()
        pct = (count / len(df) * 100) if len(df) > 0 else 0.0
        return ValidationRuleResult(
            rule_name="transaction_type_validity",
            passed=(count == 0),
            failing_records_count=int(count),
            failing_percentage=round(pct, 4),
            description="Transaction types must match the 5 allowed PaySim types.",
        )

    @classmethod
    def check_fraud_labels(cls, df: pd.DataFrame) -> ValidationRuleResult:
        invalid_labels = ~df["isFraud"].isin([0, 1])
        count = invalid_labels.sum()
        pct = (count / len(df) * 100) if len(df) > 0 else 0.0
        return ValidationRuleResult(
            rule_name="fraud_label_binary",
            passed=(count == 0),
            failing_records_count=int(count),
            failing_percentage=round(pct, 4),
            description="Fraud target indicator isFraud must be binary (0 or 1).",
        )

    @classmethod
    def check_balance_consistency(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """PaySim domain analysis: evaluate ledger discrepancies without automatic deletion.
        
        Origin error: (newbalanceOrig + amount) - oldbalanceOrg
        Destination error: (newbalanceDest - oldbalanceDest) - amount
        """
        # For outgoing transactions: CASH_OUT, TRANSFER, PAYMENT, DEBIT
        outgoing = df[df["type"].isin(["CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT"])]
        orig_discrepancy = (
            np.abs((outgoing["newbalanceOrig"] + outgoing["amount"]) - outgoing["oldbalanceOrg"]) > 0.01
        ).sum()

        dest_discrepancy = (
            np.abs((outgoing["newbalanceDest"] - outgoing["oldbalanceDest"]) - outgoing["amount"]) > 0.01
        ).sum()

        return {
            "origin_balance_inconsistencies": int(orig_discrepancy),
            "origin_inconsistency_rate": round(float(orig_discrepancy / len(outgoing) * 100), 2) if len(outgoing) > 0 else 0.0,
            "destination_balance_inconsistencies": int(dest_discrepancy),
            "destination_inconsistency_rate": round(float(dest_discrepancy / len(outgoing) * 100), 2) if len(outgoing) > 0 else 0.0,
            "preservation_policy": "Records are preserved and flagged as risk signals rather than deleted.",
        }
