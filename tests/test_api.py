from fastapi.testclient import TestClient
from finbench.api.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "FinBench API"


def test_analytics_endpoints():
    res_overview = client.get("/api/analytics/overview")
    assert res_overview.status_code == 200
    assert "total_transactions" in res_overview.json()

    res_tx = client.get("/api/analytics/transactions")
    assert res_tx.status_code == 200
    assert "by_channel" in res_tx.json()


def test_benchmarks_endpoints():
    res = client.get("/api/benchmarks")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 100

    # Test single benchmark detail
    res_detail = client.get(f"/api/benchmarks/{data[0]['id']}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == data[0]["id"]
    assert "expected_answer" in detail


def test_evaluation_endpoints():
    # Run evaluation on 5 questions
    payload = {"model_name": "finbench-expert-v1", "limit": 5}
    res = client.post("/api/evaluations", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["total_questions"] == 5

    # Check status endpoint
    res_status = client.get(f"/api/evaluations/{data['run_id']}")
    assert res_status.status_code == 200
    assert res_status.json()["run_id"] == data["run_id"]
