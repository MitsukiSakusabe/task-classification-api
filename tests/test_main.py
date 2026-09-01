from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "task-classification-api"

def test_classify_bug():
    response = client.post(
        "/classify",
        json={"text": "ログインボタンを押すとエラーになります"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "bug"
    assert data["priority"] == "medium"
    assert "reason" in data

def test_classify_blank_text():
    response = client.post(
        "/classify",
        json={"text": "　　"},
    )

    assert response.status_code == 422

def test_classify_too_long_text():
    response = client.post(
        "/classify",
        json={"text": "a" * 1001},
    )

    assert response.status_code == 422

def test_classify_min_length():
    response = client.post(
        "/classify",
        json={"text": "a"},
    )

    assert response.status_code == 200