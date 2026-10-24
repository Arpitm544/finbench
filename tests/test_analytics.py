from finbench.analytics.transactions import TransactionAnalyticsEngine
from finbench.analytics.fraud import FraudAnalyticsEngine
from finbench.analytics.statistics import FinancialStatisticalAnalyzer


def test_transaction_analytics():
    engine = TransactionAnalyticsEngine()
    summary = engine.get_summary_metrics()
    assert summary["total_transactions"] > 0
    assert summary["total_transaction_amount"] > 0
    assert summary["average_transaction_amount"] > 0

    by_channel = engine.get_volume_by_type()
    assert len(by_channel) > 0
    channel_types = [c["type"] for c in by_channel]
    assert "TRANSFER" in channel_types or "CASH_OUT" in channel_types

    percentiles = engine.get_high_value_percentiles()
    assert "p99" in percentiles.get("percentiles", {})
    engine.close()


def test_fraud_analytics():
    engine = FraudAnalyticsEngine()
    summary = engine.get_overall_fraud_metrics()
    assert "overall_fraud_rate" in summary
    assert "fraud_transactions_count" in summary
    assert summary["overall_fraud_rate"] >= 0.0

    by_type = engine.get_fraud_rate_by_type()
    assert len(by_type) > 0
    engine.close()


def test_statistical_analyzer():
    analyzer = FinancialStatisticalAnalyzer()
    ci = analyzer.calculate_fraud_rate_confidence_interval()
    assert "ci_lower_bound" in ci
    assert "ci_upper_bound" in ci
    assert ci["ci_lower_bound"] <= ci["ci_upper_bound"]

    tests = analyzer.run_amount_difference_tests()
    assert "welch_t_test" in tests
    assert "mann_whitney_u_test" in tests
    assert "effect_size" in tests
