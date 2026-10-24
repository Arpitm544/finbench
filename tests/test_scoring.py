from finbench.evaluation.scoring import BenchmarkScoringEngine


def test_numeric_tolerance_scoring():
    # Exact match
    score, feedback = BenchmarkScoringEngine.score_numeric(100.0, 100.0, tolerance=0.01)
    assert score == 1.0
    assert "Matched" in feedback

    # Within tolerance
    score, feedback = BenchmarkScoringEngine.score_numeric(100.0, 100.5, tolerance=0.01)
    assert score == 1.0

    # Outside tolerance
    score, feedback = BenchmarkScoringEngine.score_numeric(100.0, 150.0, tolerance=0.01)
    assert score == 0.0


def test_rubric_scoring():
    rubric = {
        "required_terms": ["TRANSFER", "CASH_OUT"],
        "key_points": ["unauthorized siphoning", "rapid liquidation"],
    }
    pred_good = "Fraud attacks occur via TRANSFER and CASH_OUT, involving unauthorized siphoning of balances and rapid liquidation into cash."
    score, feedback = BenchmarkScoringEngine.score_rubric("TRANSFER and CASH_OUT", pred_good, rubric)
    assert score >= 0.70

    pred_bad = "Credit cards have high fraud."
    score_bad, _ = BenchmarkScoringEngine.score_rubric("TRANSFER and CASH_OUT", pred_bad, rubric)
    assert score_bad < 0.50


def test_contradictory_evaluation_scoring():
    rubric = {
        "expected_decision": "STRICTER_RULES",
        "key_points": ["high loss ratio", "wide net"],
    }
    # Correct decision with sound reasoning
    score, status, feedback = BenchmarkScoringEngine.score_benchmark(
        evaluation_method="contradictory_evaluation",
        expected="STRICTER_RULES",
        predicted="We recommend STRICTER_RULES to cast a wide net against catastrophic fraud loss with high loss ratio.",
        rubric=rubric,
    )
    assert score >= 0.70
    assert status == "passed"
