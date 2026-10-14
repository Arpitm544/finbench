import hashlib
import logging
import time
from pathlib import Path
from typing import Dict, Any, Generator, Optional
import polars as pl
import pandas as pd
from sqlalchemy.orm import Session

from finbench.config import settings
from finbench.database import SessionLocal, Transaction, engine, init_db

logger = logging.getLogger(__name__)


def generate_stable_transaction_id(step: int, row_index: int, name_orig: str, name_dest: str, amount: float) -> str:
    """Generate deterministic, unique transaction ID for PaySim records."""
    token = f"{step}:{row_index}:{name_orig}:{name_dest}:{amount:.2f}".encode("utf-8")
    short_hash = hashlib.sha256(token).hexdigest()[:8]
    return f"TXN-S{step:04d}-{row_index:07d}-{short_hash}"


class ChunkedDataLoader:
    """Loads massive financial transaction datasets into PostgreSQL / SQLite in memory-efficient chunks."""

    def __init__(self, chunk_size: int = 50000, dataset_version: str = "v1"):
        self.chunk_size = chunk_size
        self.dataset_version = dataset_version

    def load_csv_in_chunks(
        self,
        csv_path: Path,
        max_rows: Optional[int] = None,
        truncate_first: bool = False,
    ) -> Dict[str, Any]:
        """Read CSV in streaming batches and persist into database."""
        init_db()
        start_time = time.time()
        logger.info(f"Beginning chunked ingestion from {csv_path} (chunk_size={self.chunk_size:,})...")

        if truncate_first:
            logger.warning("Truncating existing transactions table...")
            with SessionLocal() as session:
                session.query(Transaction).delete()
                session.commit()

        total_rows_inserted = 0
        chunk_idx = 0

        # Read CSV using pandas chunksize iterator or Polars
        for chunk in pd.read_csv(csv_path, chunksize=self.chunk_size):
            chunk_start = time.time()
            chunk_records = []
            
            for idx, row in chunk.iterrows():
                if max_rows and total_rows_inserted >= max_rows:
                    break

                tx_id = generate_stable_transaction_id(
                    step=int(row["step"]),
                    row_index=total_rows_inserted,
                    name_orig=str(row["nameOrig"]),
                    name_dest=str(row["nameDest"]),
                    amount=float(row["amount"]),
                )

                record = {
                    "transaction_id": tx_id,
                    "step": int(row["step"]),
                    "type": str(row["type"]),
                    "amount": float(row["amount"]),
                    "name_orig": str(row["nameOrig"]),
                    "oldbalance_org": float(row["oldbalanceOrg"]),
                    "newbalance_orig": float(row["newbalanceOrig"]),
                    "name_dest": str(row["nameDest"]),
                    "oldbalance_dest": float(row["oldbalanceDest"]),
                    "newbalance_dest": float(row["newbalanceDest"]),
                    "is_fraud": int(row["isFraud"]),
                    "is_flagged_fraud": int(row.get("isFlaggedFraud", 0)),
                    "dataset_version": self.dataset_version,
                }
                chunk_records.append(record)
                total_rows_inserted += 1

            # Insert batch into database
            if chunk_records:
                with engine.begin() as conn:
                    conn.execute(Transaction.__table__.insert(), chunk_records)

            chunk_idx += 1
            elapsed_chunk = time.time() - chunk_start
            logger.info(
                f"Chunk {chunk_idx}: Inserted {len(chunk_records):,} rows in {elapsed_chunk:.2f}s "
                f"(Total: {total_rows_inserted:,})"
            )

            if max_rows and total_rows_inserted >= max_rows:
                logger.info(f"Reached specified limit of {max_rows:,} rows.")
                break

        total_elapsed = time.time() - start_time
        rate = total_rows_inserted / total_elapsed if total_elapsed > 0 else 0
        logger.info(
            f"Ingestion completed: {total_rows_inserted:,} rows loaded in {total_elapsed:.2f}s "
            f"({rate:,.1f} rows/sec)."
        )

        return {
            "total_rows": total_rows_inserted,
            "duration_seconds": round(total_elapsed, 2),
            "throughput_rows_per_sec": round(rate, 1),
            "chunks_processed": chunk_idx,
            "dataset_version": self.dataset_version,
        }
