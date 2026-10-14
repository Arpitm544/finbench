import logging
from pathlib import Path
from typing import Optional, Dict, Any

from finbench.config import settings
from finbench.ingestion.download import ensure_dataset, generate_synthetic_paysim
from finbench.ingestion.loader import ChunkedDataLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def run_ingestion_pipeline(
    csv_path: Optional[Path] = None,
    sample_records: int = 50000,
    chunk_size: int = 25000,
    max_rows: Optional[int] = None,
    truncate_first: bool = False,
    dataset_version: str = "v1",
) -> Dict[str, Any]:
    """Execute end-to-end dataset acquisition and chunked database loading."""
    logger.info("Starting FinBench Ingestion Pipeline...")

    # Ensure dataset is available
    active_path = csv_path or ensure_dataset(sample_records=sample_records)
    logger.info(f"Target dataset file: {active_path}")

    # Load into database
    loader = ChunkedDataLoader(chunk_size=chunk_size, dataset_version=dataset_version)
    result = loader.load_csv_in_chunks(
        csv_path=active_path,
        max_rows=max_rows,
        truncate_first=truncate_first,
    )

    logger.info(f"Pipeline finished successfully. Result: {result}")
    return result


if __name__ == "__main__":
    run_ingestion_pipeline(sample_records=10000, truncate_first=True)
