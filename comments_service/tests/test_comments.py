# comments_service/tests/test_comments.py

import pytest
from fastapi.testclient import TestClient
import json
from comments_service import main  # Импортируем приложение из comments_service/main.py


# --- Фейковые реализации для комментариев ---
class FakeCursorComments:
    def __init__(self, db):
        self.db = db
        self.result = None

    def execute(self, query, params):
        # Вставка нового комментария
        if query.startswith("INSERT INTO comments"):
            new_id = self.db["next_id"]
            self.db["next_id"] += 1
            post_id, content, is_approved = params
            self.db["comments"][new_id] = {
                "id": new_id,
                "post_id": post_id,
                "content": content,
                "is_approved": is_approved,
            }
            self.result = (new_id,)
        # Получение комментариев для заданного post_id
        elif query.startswith(
            "SELECT id, post_id, content, is_approved FROM comments WHERE post_id ="
        ):
            post_id = params[0]
            results = []
            for comment in self.db["comments"].values():
                if comment["post_id"] == post_id:
                    results.append(
                        (
                            comment["id"],
                            comment["post_id"],
                            comment["content"],
                            comment["is_approved"],
                        )
                    )
            self.result = results

    def fetchone(self):
        return self.result

    def fetchall(self):
        if isinstance(self.result, list):
            return self.result
        return [self.result] if self.result is not None else []

    def close(self):
        pass


class FakeConnectionComments:
    def __init__(self, db):
        self.db = db

    def cursor(self):
        return FakeCursorComments(self.db)

    def commit(self):
        pass

    def close(self):
        pass


@pytest.fixture
def fake_comments_db():
    # Чистая in-memory БД для комментариев
    return {"next_id": 1, "comments": {}}


@pytest.fixture
def override_get_connection(fake_comments_db, monkeypatch):
    def fake_get_connection():
        return FakeConnectionComments(fake_comments_db)

    monkeypatch.setattr(main, "get_connection", fake_get_connection)


# Фейковый ответ для вызова sentiment_service (переопределяем requests.post)
class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


def fake_requests_post(url, json):
    # Независимо от входных данных возвращаем положительный анализ
    return FakeResponse({"sentiment": "positive"}, status_code=200)


@pytest.fixture
def override_requests_post(monkeypatch):
    monkeypatch.setattr(
        main, "requests", type("FakeRequests", (), {"post": fake_requests_post})
    )


@pytest.fixture
def client(override_get_connection, override_requests_post):
    return TestClient(main.app)


# --- Тесты эндпоинтов ---
def test_create_comment(client):
    # Для теста комментариев нужен post_id – в тестовом окружении можно условно задать его значение
    post_id = 1  # допустим, есть пост с id = 1
    comment_data = {"post_id": post_id, "content": "Отличная статья!"}
    response = client.post("/comments", json=comment_data)
    assert response.status_code == 200, response.text
    comment = response.json()
    assert comment["post_id"] == post_id
    assert comment["content"] == comment_data["content"]
    # Фиксированная переопределённая логика sentiment возвращает "positive", значит is_approved должно быть True
    assert comment["is_approved"] is True


def test_list_comments(client):
    post_id = 2
    # Создаем два комментария для одного post_id
    comment1 = {"post_id": post_id, "content": "Первый комментарий"}
    comment2 = {"post_id": post_id, "content": "Второй комментарий"}
    response1 = client.post("/comments", json=comment1)
    response2 = client.post("/comments", json=comment2)
    assert response1.status_code == 200, response1.text
    assert response2.status_code == 200, response2.text

    # Запрос списка комментариев
    response = client.get(f"/comments/{post_id}")
    assert response.status_code == 200, response.text
    comments = response.json()
    contents = [c["content"] for c in comments]
    assert "Первый комментарий" in contents
    assert "Второй комментарий" in contents
