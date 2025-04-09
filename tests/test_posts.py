import requests

BASE_URL = "http://localhost:8001"

def test_create_and_get_post():
    # Создаем новый пост
    post_data = {"title": "Тестовый заголовок", "content": "Тестовое содержимое"}
    create_resp = requests.post(f"{BASE_URL}/posts", json=post_data)
    assert create_resp.status_code == 200, f"Ошибка при создании поста: {create_resp.text}"
    created_post = create_resp.json()
    assert created_post["title"] == post_data["title"]
    assert created_post["content"] == post_data["content"]
    assert "edit_key_" in created_post["edit_key"]

    # Получаем созданный пост по id
    post_id = created_post["id"]
    get_resp = requests.get(f"{BASE_URL}/posts/{post_id}")
    assert get_resp.status_code == 200, f"Ошибка при получении поста: {get_resp.text}"
    fetched_post = get_resp.json()
    assert fetched_post["title"] == post_data["title"]
    assert fetched_post["content"] == post_data["content"]

def test_update_post_valid_and_invalid_edit_key():
    # Создаем новый пост
    original = {"title": "Оригинальный заголовок", "content": "Оригинальное содержимое"}
    resp = requests.post(f"{BASE_URL}/posts", json=original)
    assert resp.status_code == 200, f"Ошибка создания поста: {resp.text}"
    post = resp.json()
    post_id = post["id"]
    valid_edit_key = post["edit_key"]

    # Попытка корректного обновления поста с верным ключом
    updated = {"title": "Обновленный заголовок", "content": "Обновленное содержимое"}
    update_resp = requests.put(f"{BASE_URL}/posts/{post_id}?edit_key={valid_edit_key}", json=updated)
    assert update_resp.status_code == 200, f"Ошибка обновления поста: {update_resp.text}"
    updated_post = update_resp.json()
    assert updated_post["title"] == updated["title"]
    assert updated_post["content"] == updated["content"]

    # Попытка обновления с неверным ключом
    invalid_edit_key = "неправильный_ключ"
    bad_resp = requests.put(f"{BASE_URL}/posts/{post_id}?edit_key={invalid_edit_key}", json=updated)
    assert bad_resp.status_code == 403, "Обновление с неверным ключом должно вернуть статус 403"
