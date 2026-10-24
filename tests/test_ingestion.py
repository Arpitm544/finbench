from pathlib import Path
import pandas as pd
from finbench.ingestion.download import generate_synthetic_paysim
from finbench.ingestion.loader import generate_stable_transaction_id, ChunkedDataLoader


def test_synthetic_paysim_generation(tmp_path: Path):
    out_csv = tmp_path / "test_paysim.csv"
    res = generate_synthetic_paysim(out_csv, num_records=500, seed=123)
    assert res.exists()
    df = pd.read_csv(res)
    assert len(df) == 500
    expected_cols = {
        "step", "type", "amount", "nameOrig", "oldbalanceOrg",
        "newbalanceOrig", "nameDest", "oldbalanceDest", "newbalanceDest",
        "isFraud", "isFlaggedFraud"
    }
    assert expected_cols.issubset(set(df.columns))
    # Assert fraud only happens in TRANSFER or CASH_OUT
    fraud_types = df[df["isFraud"] == 1]["type"].unique()
    for t in fraud_types:
        assert t in ("TRANSFER", "CASH_OUT")


def test_stable_transaction_id_determinism():
    id1 = generate_stable_transaction_id(10, 50, "C123456", "M987654", 500.25)
    id2 = generate_stable_transaction_id(10, 50, "C123456", "M987654", 500.25)
    id3 = generate_stable_transaction_id(10, 51, "C123456", "M987654", 500.25)

    assert id1 == id2
    assert id1 != id3
    assert id1.startswith("TXN-S0010-0000050-")
