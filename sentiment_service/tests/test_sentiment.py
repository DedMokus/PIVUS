# sentiment_service/tests/test_sentiment.py

import pytest
from fastapi.testclient import TestClient
from sentiment_service import (
    main,
)  # Импортируем приложение из sentiment_service/main.py


@pytest.fixture
def client():
    return TestClient(main.app)


def test_sentiment_positive(client):
    # Текст с положительной эмоциональной окраской
    data = {"text": "Замечательный сервис, очень доволен работой!"}
    response = client.post("/sentiment-check", json=data)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["sentiment"] in ["positive", "negative"]


def test_sentiment_negative(client):
    # Текст с негативной окраской
    data = {"text": "Ужасный опыт, все плохо и никто не помогает."}
    response = client.post("/sentiment-check", json=data)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["sentiment"] in ["positive", "negative"]
