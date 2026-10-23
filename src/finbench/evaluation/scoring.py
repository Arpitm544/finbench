import json
import logging
import re
from typing import Dict, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class BenchmarkScoringEngine:
    """Evaluates and grades candidate model answers against verified ground truth."""

    @classmethod
    def extract_first_number(cls, text_val: Any) -> Optional[float]:
        if isinstance(text_val, (int, float)):
            return float(text_val)
        if not isinstance(text_val, str):
            return None
        # Remove commas and currency signs
        cleaned = text_val.replace(",", "").replace("$", "").replace("%", "").strip()
        match = re.search(r"[-+]?\d*\.?\d+", cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None

    @classmethod
    def score_numeric(
        cls, expected: Any, predicted: Any, tolerance: float = 0.01
    ) -> Tuple[float, str]:
        exp_num = cls.extract_first_number(expected)
        pred_num = cls.extract_first_number(predicted)

        if exp_num is None:
            return 0.0, f"Expected value {expected} is not numeric."
        if pred_num is None:
            return 0.0, f"Predicted answer '{predicted}' could not be parsed as a number."

        # Relative or absolute tolerance check
        abs_diff = abs(exp_num - pred_num)
        denom = max(1.0, abs(exp_num))
        rel_diff = abs_diff / denom

        # Accept if within tolerance
        if abs_diff <= tolerance or rel_diff <= tolerance:
            return 1.0, f"Matched expected {exp_num} (Predicted: {pred_num}, Delta: {abs_diff:.4f} <= Tol: {tolerance})"
        
        # Partial credit if within 2x tolerance
        if rel_diff <= (tolerance * 2.5):
            return 0.5, f"Partial credit: within 2.5x tolerance (Expected: {exp_num}, Predicted: {pred_num}, RelDiff: {rel_diff:.4f})"

        return 0.0, f"Exceeded tolerance (Expected: {exp_num}, Predicted: {pred_num}, Delta: {abs_diff:.4f} > Tol: {tolerance})"

    @classmethod
    def score_rubric(
        cls, expected: Any, predicted: Any, rubric: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, str]:
        pred_str = str(predicted).lower() if predicted is not None else ""
        if not pred_str:
            return 0.0, "Empty response received."

        if not rubric:
            # Fallback to substring matching on expected
            exp_str = str(expected).lower()
            if exp_str in pred_str:
                return 1.0, "Direct semantic match with reference answer."
            return 0.5, "Partial semantic alignment."

        key_points = rubric.get("key_points", [])
        required_terms = rubric.get("required_terms", [])
        expected_decision = rubric.get("expected_decision")

        score = 0.0
        feedback_notes = []

        # Check required decision
        if expected_decision:
            if expected_decision.lower() in pred_str or (
                "stricter" in pred_str if "stricter" in expected_decision.lower() else False
            ) or (
                "relaxed" in pred_str if "relaxed" in expected_decision.lower() else False
            ):
                score += 0.4
                feedback_notes.append("Correct core business decision reached.")
            else:
                feedback_notes.append(f"Failed expected decision: {expected_decision}.")

        # Check required terms
        if required_terms:
            matched_terms = [t for t in required_terms if t.lower() in pred_str]
            term_score = len(matched_terms) / len(required_terms)
            score += term_score * 0.3
            feedback_notes.append(f"Matched {len(matched_terms)}/{len(required_terms)} required domain terms.")

        # Check key conceptual points
        if key_points:
            matched_pts = 0
            for pt in key_points:
                # Simple keyword heuristic across words in point
                words = [w.lower() for w in re.findall(r"\w+", pt) if len(w) > 4]
                if any(w in pred_str for w in words):
                    matched_pts += 1
            pt_score = (matched_pts / len(key_points)) * 0.4
            score += pt_score
            feedback_notes.append(f"Covered {matched_pts}/{len(key_points)} key reasoning components.")

        final_score = min(1.0, round(score, 2))
        if final_score == 0.0 and len(pred_str) > 20:
            final_score = 0.25  # Attempt credit

        return final_score, "; ".join(feedback_notes)

    @classmethod
    def score_benchmark(
        cls,
        evaluation_method: str,
        expected: Any,
        predicted: Any,
        tolerance: float = 0.01,
        rubric: Optional[Dict[str, Any]] = None,
    ) -> Tuple[float, str, str]:
        """Main scoring dispatcher returning (score, status, feedback)."""
        if evaluation_method == "numeric_tolerance":
            score, feedback = cls.score_numeric(expected, predicted, tolerance)
        elif evaluation_method in ("rubric_scoring", "contradictory_evaluation"):
            score, feedback = cls.score_rubric(expected, predicted, rubric)
        elif evaluation_method == "statistical_verification":
            score, feedback = cls.score_numeric(expected, predicted, tolerance)
        elif evaluation_method == "sql_execution":
            score, feedback = cls.score_rubric(expected, predicted, rubric)
        else:
            score, feedback = cls.score_numeric(expected, predicted, tolerance)

        status = "passed" if score >= 0.70 else "failed"
        return score, status, feedback
