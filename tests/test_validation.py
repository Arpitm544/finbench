import pytest
import pandas as pd
from finbench.validation.schema import TransactionSchema, TransactionType
from finbench.validation.checks import FinancialDataQualityChecker


def test_transaction_schema_valid():
    tx = TransactionSchema(
        step=24,
        type=TransactionType.TRANSFER,
        amount=50000.0,
        nameOrig="C123456789",
        oldbalanceOrg=50000.0,
        newbalanceOrig=0.0,
        nameDest="C987654321",
        oldbalanceDest=0.0,
        newbalanceDest=50000.0,
        isFraud=1,
    )
    assert tx.step == 24
    assert tx.type == TransactionType.TRANSFER
    assert tx.amount == 50000.0


def test_transaction_schema_invalid_type():
    with pytest.raises(ValueError):
        TransactionSchema(
            step=1,
            type="INVALID_TYPE",
            amount=100.0,
            nameOrig="C111",
            oldbalanceOrg=100.0,
            newbalanceOrig=0.0,
            nameDest="C222",
            oldbalanceDest=0.0,
            newbalanceDest=100.0,
            isFraud=0,
        )


def test_quality_checks_on_sample(sample_df):
    missing_res = FinancialDataQualityChecker.check_missing_values(sample_df)
    assert missing_res.passed is True
    assert missing_res.failing_records_count == 0

    neg_res = FinancialDataQualityChecker.check_negative_amounts(sample_df)
    assert neg_res.passed is True

    type_res = FinancialDataQualityChecker.check_invalid_types(sample_df)
    assert type_res.passed is True

    bal_res = FinancialDataQualityChecker.check_balance_consistency(sample_df)
    assert "origin_balance_inconsistencies" in bal_res
    assert bal_res["preservation_policy"] != ""
