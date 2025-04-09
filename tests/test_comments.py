import requests

BASE_URL_POSTS = "http://localhost:8001"
BASE_URL_COMMENTS = "http://localhost:8002"

def create_post_for_comments():
    post_data = {"title": "Пост для комментариев", "content": "Содержимое поста"}
    resp = requests.post(f"{BASE_URL_POSTS}/posts", json=post_data)
    assert resp.status_code == 200, f"Ошибка создания поста: {resp.text}"
    return resp.json()

def test_create_comment():
    # Создаем пост для комментария
    post = create_post_for_comments()
    post_id = post["id"]

    # Отправляем комментарий
    comment_data = {"post_id": post_id, "content": "Отличная статья!"}
    resp = requests.post(f"{BASE_URL_COMMENTS}/comments", json=comment_data)
    assert resp.status_code == 200, f"Ошибка создания комментария: {resp.text}"
    comment = resp.json()
    assert comment["post_id"] == post_id
    assert comment["content"] == comment_data["content"]
    # В данном примере простое правило: если результат тональности не "negative", комментарий считается утверждённым
    assert "is_approved" in comment

def test_list_comments():
    post = create_post_for_comments()
    post_id = post["id"]

    # Создаем два комментария
    comment1 = {"post_id": post_id, "content": "Первый комментарий"}
    comment2 = {"post_id": post_id, "content": "Второй комментарий"}
    r1 = requests.post(f"{BASE_URL_COMMENTS}/comments", json=comment1)
    r2 = requests.post(f"{BASE_URL_COMMENTS}/comments", json=comment2)
    assert r1.status_code == 200, f"Ошибка создания комментария 1: {r1.text}"
    assert r2.status_code == 200, f"Ошибка создания комментария 2: {r2.text}"

    # Получаем все комментарии для поста
    list_resp = requests.get(f"{BASE_URL_COMMENTS}/comments/{post_id}")
    assert list_resp.status_code == 200, f"Ошибка получения списка комментариев: {list_resp.text}"
    comments = list_resp.json()
    contents = [c["content"] for c in comments]
    assert "Первый комментарий" in contents
    assert "Второй комментарий" in contents
