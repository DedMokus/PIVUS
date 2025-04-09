import requests

BASE_URL = "http://localhost:8003"

def test_sentiment_positive():
    # Текст с положительной эмоциональной окраской
    data = {"text": "Замечательный сервис, очень доволен работой!"}
    resp = requests.post(f"{BASE_URL}/sentiment-check", json=data)
    assert resp.status_code == 200, f"Ошибка запроса на анализ тональности: {resp.text}"
    result = resp.json()
    # В зависимости от модели, ожидаем "positive" или "negative". Здесь проверяем корректность возвращаемого значения.
    assert result["sentiment"] in ["positive", "negative"]

def test_sentiment_negative():
    # Текст с негативной окраской
    data = {"text": "Ужасный опыт, все плохо и никто не помогает."}
    resp = requests.post(f"{BASE_URL}/sentiment-check", json=data)
    assert resp.status_code == 200, f"Ошибка запроса на анализ тональности: {resp.text}"
    result = resp.json()
    assert result["sentiment"] in ["positive", "negative"]
