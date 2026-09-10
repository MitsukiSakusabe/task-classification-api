from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

import httpx

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
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": '{"category":"bug","priority":"medium","reason":"test"}'
    }

    with patch("main.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        response = client.post(
            "/classify",
            json={"text": "a"},
        )

        assert response.status_code == 200


def test_classify_ollama_unavailable():
    with patch("main.httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = httpx.ConnectError("connection failed")

        response = client.post(
            "/classify",
            json={"text": "ログインできません"},
        )

        assert response.status_code == 503
        assert response.json()["detail"] == "Ollama server is unavailable"

def test_classify_ollama_502():
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": '{"categroy" : "bug","priority":"medium","reason":"test"'
    }

    with patch("main.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        response = client.post(
            "/classify",
            json={"text": "Jsonが不正です"},
        )

        assert response.status_code == 502

def test_classify_missing_category():
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": '{"priority":"medium","reason":"test"}'
    }

    with patch("main.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        response = client.post(
            "/classify",
            json={"text": "Jsonが不正です"},
        )

        assert response.status_code == 502

def test_classify_ollama_502_http_error():
    error_response = Mock()
    error_response.status_code = 500

    error_request = Mock()

    with patch("main.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPStatusError(
            "Internal Server Error",
            request=error_request,
            response=error_response,
        )

        response = client.post(
            "/classify" ,
            json = {"text" : "HTTPが異常です"},
        )

        assert response.status_code == 502

def test_classify_ollama_504():
    with patch("main.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("request timed out")

        response = client.post(
            "/classify",
            json={"text": "応答がありません"},
        )

        assert response.status_code == 504


        