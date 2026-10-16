import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from finbench.config import settings
from finbench.database import SessionLocal, Transaction

logger = logging.getLogger(__name__)


class TransactionAnalyticsEngine:
    """Computes comprehensive transaction volume, value, distribution, and temporal metrics."""

    def __init__(self, db_session: Session = None):
        self.session = db_session or SessionLocal()
        self._owns_session = db_session is None

    def close(self):
        if self._owns_session:
            self.session.close()

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Module A.1, A.2, A.3: Total volume, total value, mean, median, min, max."""
        query = self.session.query(
            func.count(Transaction.id).label("total_volume"),
            func.sum(Transaction.amount).label("total_value"),
            func.avg(Transaction.amount).label("avg_value"),
            func.min(Transaction.amount).label("min_value"),
            func.max(Transaction.amount).label("max_value"),
        ).first()

        total_volume = query.total_volume or 0
        total_value = float(query.total_value or 0.0)
        avg_value = float(query.avg_value or 0.0)
        min_value = float(query.min_value or 0.0)
        max_value = float(query.max_value or 0.0)

        # Get median using numpy if rows exist
        amounts = [r[0] for r in self.session.query(Transaction.amount).limit(50000).all()]
        median_value = float(np.median(amounts)) if amounts else 0.0

        return {
            "total_transactions": total_volume,
            "total_transaction_amount": round(total_value, 2),
            "average_transaction_amount": round(avg_value, 2),
            "median_transaction_amount": round(median_value, 2),
            "min_transaction_amount": round(min_value, 2),
            "max_transaction_amount": round(max_value, 2),
        }

    def get_volume_by_type(self) -> List[Dict[str, Any]]:
        """Module A.4: Transaction count and percentage breakdown by type."""
        total = self.session.query(func.count(Transaction.id)).scalar() or 1
        records = (
            self.session.query(
                Transaction.type,
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("total_amount"),
                func.avg(Transaction.amount).label("avg_amount"),
            )
            .group_by(Transaction.type)
            .order_by(func.count(Transaction.id).desc())
            .all()
        )

        results = []
        for r in records:
            cnt = r.count
            amt = float(r.total_amount or 0.0)
            results.append({
                "type": r.type,
                "count": cnt,
                "percentage": round((cnt / total) * 100, 2),
                "total_amount": round(amt, 2),
                "avg_amount": round(float(r.avg_amount or 0.0), 2),
            })
        return results

    def get_time_series_trends(self, bucket_steps: int = 24) -> List[Dict[str, Any]]:
        """Module A.5: Transaction trends aggregated by simulated days (24 hours = 24 steps)."""
        # Bucket by step // bucket_steps
        rows = (
            self.session.query(
                (Transaction.step / bucket_steps).label("day_bucket"),
                func.count(Transaction.id).label("volume"),
                func.sum(Transaction.amount).label("total_amount"),
                func.sum(Transaction.is_fraud).label("fraud_count"),
            )
            .group_by("day_bucket")
            .order_by("day_bucket")
            .all()
        )

        trends = []
        for r in rows:
            day = int(r.day_bucket) + 1
            vol = r.volume
            frd = r.fraud_count or 0
            trends.append({
                "day": day,
                "volume": vol,
                "total_amount": round(float(r.total_amount or 0.0), 2),
                "fraud_count": frd,
                "fraud_rate": round(float(frd / vol), 6) if vol > 0 else 0.0,
            })
        return trends

    def get_high_value_percentiles(self) -> Dict[str, Any]:
        """Module A.6: High-value transaction percentile thresholds and outlier analysis."""
        amounts = np.array([r[0] for r in self.session.query(Transaction.amount).all()])
        if len(amounts) == 0:
            return {}

        p50 = float(np.percentile(amounts, 50))
        p75 = float(np.percentile(amounts, 75))
        p90 = float(np.percentile(amounts, 90))
        p95 = float(np.percentile(amounts, 95))
        p99 = float(np.percentile(amounts, 99))
        p999 = float(np.percentile(amounts, 99.9))

        high_val_count = int(np.sum(amounts >= p99))
        high_val_sum = float(np.sum(amounts[amounts >= p99]))
        total_sum = float(np.sum(amounts))

        return {
            "percentiles": {
                "p50": round(p50, 2),
                "p75": round(p75, 2),
                "p90": round(p90, 2),
                "p95": round(p95, 2),
                "p99": round(p99, 2),
                "p99_9": round(p999, 2),
            },
            "p99_threshold": round(p99, 2),
            "p99_transaction_count": high_val_count,
            "p99_share_of_total_value_pct": round((high_val_sum / total_sum * 100), 2) if total_sum > 0 else 0.0,
        }


def generate_transaction_analysis_report(output_path: Path) -> Path:
    """Generate detailed markdown report on transaction analytics."""
    engine = TransactionAnalyticsEngine()
    summary = engine.get_summary_metrics()
    by_type = engine.get_volume_by_type()
    percentiles = engine.get_high_value_percentiles()
    engine.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    table_rows = "\n".join([
        f"| `{t['type']}` | {t['count']:,} | {t['percentage']}% | ${t['total_amount']:,.2f} | ${t['avg_amount']:,.2f} |"
        for t in by_type
    ])

    content = f"""# FinBench — Financial Transaction Analytics Report

**Analytics Scope:** Complete Ingested Transaction Population  
**Total Volume:** {summary['total_transactions']:,} records  
**Total Value:** ${summary['total_transaction_amount']:,.2f}  
**Average Transaction Size:** ${summary['average_transaction_amount']:,.2f}  
**Median Transaction Size:** ${summary['median_transaction_amount']:,.2f}  

---

## 1. Transaction Volume & Liquidity by Channel

Financial transactions are segmented across five primary operational payment and settlement channels:

| Transaction Type | Volume Count | Volume Share | Gross Volume ($) | Average Amount ($) |
| :--- | :--- | :--- | :--- | :--- |
{table_rows}

---

## 2. High-Value Tail Analysis & Skewness

Transaction amounts exhibit severe positive skewness characteristic of real-world money movement networks:

- **50th Percentile (Median):** ${percentiles.get('percentiles', {}).get('p50', 0):,.2f}
- **90th Percentile:** ${percentiles.get('percentiles', {}).get('p90', 0):,.2f}
- **95th Percentile:** ${percentiles.get('percentiles', {}).get('p95', 0):,.2f}
- **99th Percentile:** ${percentiles.get('percentiles', {}).get('p99', 0):,.2f}
- **99.9th Percentile:** ${percentiles.get('percentiles', {}).get('p99_9', 0):,.2f}

> [!IMPORTANT]
> The top 1% of transactions (`P99` cutoff at **${percentiles.get('p99_threshold', 0):,.2f}**) account for **{percentiles.get('p99_share_of_total_value_pct', 0)}%** of gross network volume. Fraud mitigation rules targeting high-value thresholds must balance capital preservation with customer friction.
"""
    output_path.write_text(content)
    return output_path
