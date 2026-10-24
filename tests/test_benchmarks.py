from finbench.benchmarks.templates import BENCHMARK_CATALOG
from finbench.benchmarks.generator import generate_retired_question_registry, generate_data_owner_interview_questionnaire
from finbench.benchmarks.schemas import BenchmarkQuestionModel


def test_catalog_100_questions():
    assert len(BENCHMARK_CATALOG) == 100
    ids = [q["id"] for q in BENCHMARK_CATALOG]
    assert len(set(ids)) == 100  # Unique IDs
    for item in BENCHMARK_CATALOG:
        model = BenchmarkQuestionModel(**item)
        assert model.id.startswith("FIN-")


def test_category_distribution():
    from collections import Counter
    cats = Counter([q["category"] for q in BENCHMARK_CATALOG])
    assert cats["advanced_sql"] == 25
    assert cats["financial_statistics"] == 15
    assert cats["fraud_analysis"] == 20
    assert cats["risk_assessment"] == 15
    assert cats["business_decisions"] == 10
    assert cats["data_quality"] == 5
    assert cats["contradictory_evidence"] == 10


def test_retired_question_registry():
    retired = generate_retired_question_registry()
    assert len(retired) >= 5
    for r in retired:
        assert "question_id" in r
        assert "data_owner" in r
        assert "retirement_reason" in r
        assert "replacement_question_id" in r


def test_data_owner_interview_questionnaire():
    interview = generate_data_owner_interview_questionnaire()
    assert "questions" in interview
    assert len(interview["questions"]) >= 4
