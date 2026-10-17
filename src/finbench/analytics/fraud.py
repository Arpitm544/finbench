import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from finbench.config import settings
from finbench.database import SessionLocal, Transaction

logger = logging.getLogger(__name__)


class FraudAnalyticsEngine:
    """Specialized analytical engine for fraud patterns, loss accounting, and concentration."""

    def __init__(self, db_session: Session = None):
        self.session = db_session or SessionLocal()
        self._owns_session = db_session is None

    def close(self):
        if self._owns_session:
            self.session.close()

    def get_overall_fraud_metrics(self) -> Dict[str, Any]:
        """Module B.1 & B.3: Overall fraud rate and aggregate fraudulent value."""
        total_tx = self.session.query(func.count(Transaction.id)).scalar() or 0
        total_value = float(self.session.query(func.sum(Transaction.amount)).scalar() or 0.0)

        fraud_stats = self.session.query(
            func.count(Transaction.id).label("fraud_count"),
            func.sum(Transaction.amount).label("fraud_value"),
            func.avg(Transaction.amount).label("avg_fraud_amount"),
            func.max(Transaction.amount).label("max_fraud_amount"),
        ).filter(Transaction.is_fraud == 1).first()

        fraud_count = fraud_stats.fraud_count or 0
        fraud_value = float(fraud_stats.fraud_value or 0.0)
        avg_fraud = float(fraud_stats.avg_fraud_amount or 0.0)
        max_fraud = float(fraud_stats.max_fraud_amount or 0.0)

        fraud_rate = (fraud_count / total_tx) if total_tx > 0 else 0.0
        fraud_value_pct = (fraud_value / total_value * 100) if total_value > 0 else 0.0

        return {
            "total_transactions": total_tx,
            "fraud_transactions_count": fraud_count,
            "overall_fraud_rate": round(fraud_rate, 6),
            "overall_fraud_rate_percentage": round(fraud_rate * 100, 4),
            "fraud_rate_basis_points": round(fraud_rate * 10000, 2),
            "total_fraud_loss_amount": round(fraud_value, 2),
            "fraud_value_share_pct": round(fraud_value_pct, 2),
            "average_fraud_amount": round(avg_fraud, 2),
            "max_fraud_amount": round(max_fraud, 2),
        }

    def get_fraud_rate_by_type(self) -> List[Dict[str, Any]]:
        """Module B.2: Fraud prevalence by payment channel (TRANSFER vs CASH_OUT vs others)."""
        records = (
            self.session.query(
                Transaction.type,
                func.count(Transaction.id).label("total_volume"),
                func.sum(Transaction.is_fraud).label("fraud_count"),
                func.sum(Transaction.amount).label("total_amount"),
                func.sum(
                    case((Transaction.is_fraud == 1, Transaction.amount), else_=0.0)
                ).label("fraud_amount"),
            )
            .group_by(Transaction.type)
            .order_by(func.sum(Transaction.is_fraud).desc())
            .all()
        )

        results = []
        for r in records:
            vol = r.total_volume
            frd = r.fraud_count or 0
            frd_amt = float(r.fraud_amount or 0.0)
            rate = (frd / vol) if vol > 0 else 0.0

            results.append({
                "type": r.type,
                "total_volume": vol,
                "fraud_count": frd,
                "fraud_rate_pct": round(rate * 100, 4),
                "total_amount": round(float(r.total_amount or 0.0), 2),
                "fraud_amount": round(frd_amt, 2),
                "fraud_amount_share_pct": round((frd_amt / float(r.total_amount or 1.0)) * 100, 2),
            })
        return results

    def get_fraud_concentration_by_account(self, top_n: int = 10) -> Dict[str, Any]:
        """Module B.6: Identification of high-frequency mule originators and destinations."""
        top_dest_mules = (
            self.session.query(
                Transaction.name_dest,
                func.count(Transaction.id).label("fraud_count"),
                func.sum(Transaction.amount).label("fraud_total_inflow"),
            )
            .filter(Transaction.is_fraud == 1)
            .group_by(Transaction.name_dest)
            .order_by(func.count(Transaction.id).desc(), func.sum(Transaction.amount).desc())
            .limit(top_n)
            .all()
        )

        top_dest_list = [
            {
                "account": r.name_dest,
                "fraud_incidents": r.fraud_count,
                "fraud_value": round(float(r.fraud_total_inflow or 0.0), 2),
            }
            for r in top_dest_mules
        ]

        # Check FlaggedFraud disparity (how many frauds were caught by the naive simulation rule)
        flagged_count = self.session.query(func.sum(Transaction.is_flagged_fraud)).scalar() or 0
        true_fraud = self.session.query(func.sum(Transaction.is_fraud)).scalar() or 0
        rule_recall = (flagged_count / true_fraud) if true_fraud > 0 else 0.0

        return {
            "top_destination_mules": top_dest_list,
            "simulation_is_flagged_count": int(flagged_count),
            "true_fraud_count": int(true_fraud),
            "simulation_rule_recall": round(rule_recall, 4),
        }


def generate_fraud_analysis_report(output_path: Path) -> Path:
    """Generate professional Markdown documentation for fraud analytics."""
    engine = FraudAnalyticsEngine()
    summary = engine.get_overall_fraud_metrics()
    by_type = engine.get_fraud_rate_by_type()
    concentration = engine.get_fraud_concentration_by_account()
    engine.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    table_rows = "\n".join([
        f"| `{t['type']}` | {t['total_volume']:,} | {t['fraud_count']:,} | **{t['fraud_rate_pct']}%** | ${t['fraud_amount']:,.2f} |"
        for t in by_type
    ])

    content = f"""# FinBench — Financial Fraud Analytics & Loss Accounting Report

**Analytics Domain:** Financial Transaction Fraud Vulnerability  
**Dataset Population:** {summary['total_transactions']:,} records  
**Confirmed Fraudulent Transactions:** {summary['fraud_transactions_count']:,}  
**Network Fraud Prevalence:** **{summary['overall_fraud_rate_percentage']}%** ({summary['fraud_rate_basis_points']} bps)  
**Total Realized Financial Losses:** **${summary['total_fraud_loss_amount']:,.2f}**  
**Loss Share of Total Volume:** **{summary['fraud_value_share_pct']}%**  

---

## 1. Channel-Specific Fraud Vulnerability

An empirical breakdown of fraudulent activities across transaction types:

| Channel Type | Total Volume | Fraud Incidents | Fraud Rate (%) | Gross Fraud Loss ($) |
| :--- | :--- | :--- | :--- | :--- |
{table_rows}

> [!IMPORTANT]
> **Key Domain Finding:** In the PaySim environment, fraud is exclusively confined to two operational modalities:
> 1. `TRANSFER`: Primary attack vector for unauthorized funds exfiltration from victim accounts.
> 2. `CASH_OUT`: Secondary liquidation vector where compromised balances are withdrawn from the financial network.
> `PAYMENT`, `CASH_IN`, and `DEBIT` exhibit a 0.0% fraud incident rate.

---

## 2. Legacy Rule Disparity vs. Realized Fraud

The baseline simulation rule (`isFlaggedFraud`), which triggers only on single transfers exceeding $200,000, shows substantial detection disparity:

- **True Fraud Incidents:** {concentration['true_fraud_count']:,}
- **Simulation Rule Flagged:** {concentration['simulation_is_flagged_count']:,}
- **Legacy Rule Sensitivity (Recall):** **{concentration['simulation_rule_recall'] * 100:.2f}%**

> [!WARNING]
> Simple static threshold filters miss over 90% of sophisticated fraud attempts. Advanced machine learning classifiers and behavioral graph indicators are necessary to protect assets without introducing excessive false positive friction.
"""
    output_path.write_text(content)
    return output_path
