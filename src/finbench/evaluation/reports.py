import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from finbench.config import settings

logger = logging.getLogger(__name__)


def generate_evaluation_json_report(
    eval_results: Dict[str, Any], output_path: Path
) -> Path:
    """Save full AI evaluation results to JSON artifact."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(eval_results, f, indent=2)
    logger.info(f"Saved evaluation JSON report to: {output_path}")
    return output_path
