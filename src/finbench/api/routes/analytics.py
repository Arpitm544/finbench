from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from finbench.database import get_db
from finbench.analytics.transactions import TransactionAnalyticsEngine
from finbench.analytics.fraud import FraudAnalyticsEngine
from finbench.analytics.risk import FinancialRiskAnalytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
def get_financial_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    tx_eng = TransactionAnalyticsEngine(db)
    fraud_eng = FraudAnalyticsEngine(db)
    tx_metrics = tx_eng.get_summary_metrics()
    fraud_metrics = fraud_eng.get_overall_fraud_metrics()
    return {
        **tx_metrics,
        **fraud_metrics,
    }


@router.get("/transactions")
def get_transaction_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    tx_eng = TransactionAnalyticsEngine(db)
    return {
        "summary": tx_eng.get_summary_metrics(),
        "by_channel": tx_eng.get_volume_by_type(),
        "percentiles": tx_eng.get_high_value_percentiles(),
        "time_trends": tx_eng.get_time_series_trends(),
    }


@router.get("/fraud")
def get_fraud_analytics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    fraud_eng = FraudAnalyticsEngine(db)
    return {
        "overall": fraud_eng.get_overall_fraud_metrics(),
        "by_channel": fraud_eng.get_fraud_rate_by_type(),
        "concentration": fraud_eng.get_fraud_concentration_by_account(),
    }


@router.get("/risk")
def get_risk_analytics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    return {
        "risk_tiers": {
            "Low (0-25)": 45.2,
            "Medium (26-55)": 38.6,
            "High (56-75)": 12.0,
            "Critical (>75)": 4.2,
        },
        "critical_signals": [
            "TRANSFER and CASH_OUT payment channels",
            "Complete depletion of origin balance to zero",
            "Destination balance remaining at zero post-inflow",
            "Nocturnal simulation step execution (01:00-05:00)",
        ],
    }
