# posts_service/tests/test_posts.py

import pytest
from fastapi.testclient import TestClient
from posts_service import main  # Импортируем приложение из posts_service/main.py


# --- Фейковые реализации для БД ---
class FakeCursor:
    def __init__(self, db):
        self.db = db
        self.result = None

    def execute(self, query, params):
        # Обработка запроса на добавление поста
        if query.startswith("INSERT INTO posts"):
            new_id = self.db["next_id"]
            self.db["next_id"] += 1
            title, content, edit_key = params
            self.db["posts"][new_id] = {
                "id": new_id,
                "title": title,
                "content": content,
                "edit_key": edit_key,
            }
            self.result = (new_id,)
        # Выбор поста по id
        elif query.startswith(
            "SELECT id, title, content, edit_key FROM posts WHERE id ="
        ):
            post_id = params[0]
            post = self.db["posts"].get(post_id)
            self.result = (
                (post["id"], post["title"], post["content"], post["edit_key"])
                if post
                else None
            )
        # Выбор ключа редактирования
        elif query.startswith("SELECT edit_key FROM posts WHERE id ="):
            post_id = params[0]
            post = self.db["posts"].get(post_id)
            self.result = (post["edit_key"],) if post else None
        # Обновление поста по id
        elif query.startswith("UPDATE posts SET title ="):
            title, content, post_id = params
            if post_id in self.db["posts"]:
                post = self.db["posts"][post_id]
                post["title"] = title
                post["content"] = content
                self.result = (
                    post["id"],
                    post["title"],
                    post["content"],
                    post["edit_key"],
                )

    def fetchone(self):
        return self.result

    def fetchall(self):
        return (
            self.result
            if isinstance(self.result, list)
            else ([self.result] if self.result is not None else [])
        )

    def close(self):
        pass


class FakeConnection:
    def __init__(self, db):
        self.db = db

    def cursor(self):
        return FakeCursor(self.db)

    def commit(self):
        pass

    def close(self):
        pass


@pytest.fixture
def fake_posts_db():
    # Каждый тест получает собственное чистое хранилище постов
    return {"next_id": 1, "posts": {}}


@pytest.fixture
def override_get_connection(fake_posts_db, monkeypatch):
    def fake_get_connection():
        return FakeConnection(fake_posts_db)

    # Переопределяем функцию в модуле posts_service/main.py
    monkeypatch.setattr(main, "get_connection", fake_get_connection)


@pytest.fixture
def client(override_get_connection):
    return TestClient(main.app)


# --- Тесты эндпоинтов ---
def test_create_and_get_post(client):
    # Создание поста
    post_data = {"title": "Тестовый заголовок", "content": "Тестовое содержимое"}
    response = client.post("/posts", json=post_data)
    assert response.status_code == 200, response.text
    created_post = response.json()
    assert created_post["title"] == post_data["title"]
    assert created_post["content"] == post_data["content"]
    assert "edit_key_" in created_post["edit_key"]

    # Получение созданного поста
    post_id = created_post["id"]
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200, response.text
    fetched_post = response.json()
    assert fetched_post["title"] == post_data["title"]
    assert fetched_post["content"] == post_data["content"]


def test_update_post(client):
    # Сначала создаем пост
    post_data = {
        "title": "Оригинальный заголовок",
        "content": "Оригинальное содержимое",
    }
    response = client.post("/posts", json=post_data)
    created_post = response.json()
    post_id = created_post["id"]
    valid_edit_key = created_post["edit_key"]

    # Обновляем пост с правильным ключом
    updated_data = {
        "title": "Обновленный заголовок",
        "content": "Обновленное содержимое",
    }
    response = client.put(
        f"/posts/{post_id}?edit_key={valid_edit_key}", json=updated_data
    )
    assert response.status_code == 200, response.text
    updated_post = response.json()
    assert updated_post["title"] == updated_data["title"]
    assert updated_post["content"] == updated_data["content"]

    # Попытка обновления с неверным ключом
    response = client.put(f"/posts/{post_id}?edit_key=invalid_key", json=updated_data)
    assert response.status_code == 403
