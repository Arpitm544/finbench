import hashlib
import logging
import os
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

from finbench.config import settings

logger = logging.getLogger(__name__)


def generate_synthetic_paysim(
    output_path: Path,
    num_records: int = 100000,
    seed: int = 42,
    fraud_rate: float = 0.0013,  # ~0.13% realistic PaySim fraud rate
) -> Path:
    """Generate high-fidelity synthetic financial transactions matching PaySim distributions.
    
    PaySim distribution properties:
    - 5 types: PAYMENT (~34%), CASH_OUT (~35%), CASH_IN (~22%), TRANSFER (~8%), DEBIT (~1%)
    - Fraud happens ONLY in TRANSFER and CASH_OUT types
    - Steps range from 1 to 744 (representing 31 days, 24 hours per day)
    - Amounts are log-normally distributed with typical range $1 to $10,000,000
    - Balances follow origin and destination ledger movements
    """
    logger.info(f"Generating {num_records:,} synthetic PaySim records at {output_path}...")
    np.random.seed(seed)

    types = ["PAYMENT", "CASH_OUT", "CASH_IN", "TRANSFER", "DEBIT"]
    type_probs = [0.34, 0.35, 0.22, 0.08, 0.01]
    chosen_types = np.random.choice(types, size=num_records, p=type_probs)

    steps = np.random.randint(1, 745, size=num_records)

    # Log-normal transaction amounts
    amounts = np.round(np.random.lognormal(mean=8.5, sigma=1.8, size=num_records), 2)
    amounts = np.clip(amounts, 0.01, 15000000.0)

    # Customer accounts start with 'C', Merchants start with 'M'
    orig_ids = [f"C{np.random.randint(100000000, 999999999)}" for _ in range(num_records)]
    
    # Destination accounts: Merchants for PAYMENT, Customers for others
    dest_ids = []
    for t in chosen_types:
        if t == "PAYMENT" and np.random.rand() > 0.3:
            dest_ids.append(f"M{np.random.randint(100000000, 999999999)}")
        else:
            dest_ids.append(f"C{np.random.randint(100000000, 999999999)}")

    # Initial sender balances
    old_balance_org = np.round(np.random.exponential(scale=50000, size=num_records), 2)
    new_balance_orig = np.zeros(num_records)

    old_balance_dest = np.round(np.random.exponential(scale=100000, size=num_records), 2)
    new_balance_dest = np.zeros(num_records)

    is_fraud = np.zeros(num_records, dtype=int)
    is_flagged_fraud = np.zeros(num_records, dtype=int)

    # Fraud determination: only TRANSFER and CASH_OUT can be fraud
    for i in range(num_records):
        t = chosen_types[i]
        amt = amounts[i]

        if t in ("TRANSFER", "CASH_OUT") and np.random.rand() < (fraud_rate * 4.0):
            is_fraud[i] = 1
            # In PaySim fraud, origin account is frequently emptied out
            old_balance_org[i] = amt if np.random.rand() > 0.2 else old_balance_org[i]
            new_balance_orig[i] = 0.0
            
            # Recipient balance often increases or shows abnormal zero destination balance
            if np.random.rand() > 0.4:
                new_balance_dest[i] = old_balance_dest[i] + amt
            else:
                new_balance_dest[i] = 0.0  # Emptied to another mule

            if amt > 200000 and np.random.rand() > 0.7:
                is_flagged_fraud[i] = 1
        else:
            # Normal ledger balance transitions
            if t in ("CASH_OUT", "PAYMENT", "TRANSFER", "DEBIT"):
                new_balance_orig[i] = max(0.0, round(old_balance_org[i] - amt, 2))
                new_balance_dest[i] = round(old_balance_dest[i] + amt, 2)
            elif t == "CASH_IN":
                new_balance_orig[i] = round(old_balance_org[i] + amt, 2)
                new_balance_dest[i] = max(0.0, round(old_balance_dest[i] - amt, 2))

    df = pd.DataFrame({
        "step": steps,
        "type": chosen_types,
        "amount": amounts,
        "nameOrig": orig_ids,
        "oldbalanceOrg": old_balance_org,
        "newbalanceOrig": new_balance_orig,
        "nameDest": dest_ids,
        "oldbalanceDest": old_balance_dest,
        "newbalanceDest": new_balance_dest,
        "isFraud": is_fraud,
        "isFlaggedFraud": is_flagged_fraud,
    })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Successfully generated {len(df):,} transactions. Fraud records: {df['isFraud'].sum():,}")
    return output_path


def ensure_dataset(
    preferred_path: Optional[Path] = None,
    sample_records: int = 50000,
) -> Path:
    """Ensure a dataset exists: use existing raw CSV or generate a calibrated sample."""
    target_raw = preferred_path or (settings.DATA_RAW_DIR / "paysim.csv")
    if target_raw.exists() and target_raw.stat().st_size > 1024:
        logger.info(f"Using existing dataset at: {target_raw}")
        return target_raw

    # Check sample dataset
    sample_path = settings.DATA_SAMPLES_DIR / "sample_transactions.csv"
    if sample_path.exists() and sample_path.stat().st_size > 1024:
        logger.info(f"Using existing sample dataset at: {sample_path}")
        return sample_path

    logger.info(f"Dataset not found at {target_raw}. Generating {sample_records:,} sample records...")
    return generate_synthetic_paysim(sample_path, num_records=sample_records)
