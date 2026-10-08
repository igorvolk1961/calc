import pytest
from fastapi.testclient import TestClient

from calculator.api import history
from calculator.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clear_history():
    history.clear()
    yield
    history.clear()


def test_calculate_success() -> None:
    response = client.post("/api/calculate", json={"expression": "2 + 3 * (4 - 1)"})
    assert response.status_code == 200
    data = response.json()
    assert data["expression"] == "2 + 3 * (4 - 1)"
    assert data["result"] == 11.0
    assert data["result_text"] == "11"


def test_calculate_float_result_text() -> None:
    response = client.post("/api/calculate", json={"expression": "10 / 4"})
    assert response.status_code == 200
    assert response.json()["result_text"] == "2.5"


@pytest.mark.parametrize("expression", ["1/0", "2(3)", "sqrt(9", "foo"])
def test_calculate_bad_request(expression: str) -> None:
    response = client.post("/api/calculate", json={"expression": expression})
    assert response.status_code == 400
    assert response.json()["detail"]


def test_calculate_empty_expression_rejected() -> None:
    response = client.post("/api/calculate", json={"expression": ""})
    assert response.status_code == 422


def test_body_too_large_rejected() -> None:
    response = client.post("/api/calculate", json={"expression": "1" * 20000})
    assert response.status_code == 413


def test_history_accumulates_newest_first() -> None:
    for expression in ["1 + 1", "2 + 2", "3 + 3"]:
        client.post("/api/calculate", json={"expression": expression})
    response = client.get("/api/history")
    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["expression"] for item in items] == ["3 + 3", "2 + 2", "1 + 1"]
    assert items[0]["result"] == 6.0
    assert items[0]["created_at"]


def test_history_limit() -> None:
    for expression in ["1 + 1", "2 + 2", "3 + 3"]:
        client.post("/api/calculate", json={"expression": expression})
    response = client.get("/api/history", params={"limit": 1})
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["expression"] == "3 + 3"


def test_history_limit_validation() -> None:
    assert client.get("/api/history", params={"limit": 0}).status_code == 422
    assert client.get("/api/history", params={"limit": 999}).status_code == 422


def test_clear_history() -> None:
    client.post("/api/calculate", json={"expression": "1 + 1"})
    response = client.delete("/api/history")
    assert response.status_code == 204
    assert client.get("/api/history").json()["items"] == []


def test_index_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Калькулятор" in response.text
