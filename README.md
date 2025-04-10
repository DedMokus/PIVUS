# 📦 PIVUS: Платформа анонимных постов и комментариев с анализом тональности
PIVUS — это микросервисная система для публикации анонимных постов и комментариев с автоматической фильтрацией по тональности текста. Система предназначена для прототипирования социальной платформы с модерацией на основе нейросетевого анализа настроения на русском языке.

## 1. Назначение и структура системы
Система состоит из трёх микросервисов:

posts_service — управление анонимными постами (создание, получение, редактирование по ключу).

comments_service — добавление комментариев к постам с автоматическим анализом их тональности.

sentiment_service — нейросетевой анализатор тональности текста (positive/negative) на русском языке.

База данных (PostgreSQL) используется всеми сервисами совместно.

## 2. Архитектура и зависимости
🧱 Технологии и библиотеки:

* FastAPI — реализация API.
* PostgreSQL — база данных.
* Docker / Docker Compose — контейнеризация и оркестрация.
* Transformers + ONNXRuntime — инференс модели тональности.
* pytest — юнит-тесты и интеграционные тесты.


## 3. Способы запуска
⚡ Запуск через Docker
```bash
docker-compose up --build
```
После запуска:

posts_service: http://localhost:8001
comments_service: http://localhost:8002
sentiment_service: http://localhost:8003

### 🐍 Альтернативный запуск без Docker
Создайте и активируйте виртуальное окружение:

```bash
bash setup.sh
```
Затем по очереди запускать каждый сервис из соответствующей директории:

```bash
cd posts_service
uvicorn main:app --reload --port 8001
```
(Аналогично для других сервисов: comments_service, sentiment_service)

### 🌍 Переменные окружения
Передаются через docker-compose:

| Переменная         | Описание                         | Значение по умолчанию                                  |
|--------------------|----------------------------------|--------------------------------------------------------|
| POSTGRES_USER      | имя пользователя БД              | postgres_user                                          |
| POSTGRES_PASSWORD  | пароль                           | postgres_password_123                                  |
| POSTGRES_DB        | имя базы данных                  | telegraph_db                                           |
| POSTGRES_HOST      | хост БД                          | db                                                     |
| POSTGRES_PORT      | порт БД                          | 5432                                                   |
| MODEL_NAME         | имя модели Hugging Face          | cointegrated/rubert-tiny-sentiment-balanced            |
| ONNX_MODEL_PATH    | путь до ONNX модели              | /app/model.onnx                                        |
| SENTIMENT_HOST     | адрес sentiment_service          | sentiment_service                                      |
| SENTIMENT_PORT     | порт sentiment_service           | 8003                                                   |

## 4. 📖 API-документация
Все микросервисы автоматически генерируют Swagger-документацию:

http://localhost:800*/docs

### ✨ Основные эндпоинты
#### posts_service
POST /posts — создать пост

GET /posts/{id} — получить пост

PUT /posts/{id}?edit_key=... — обновить пост по ключу

#### comments_service
POST /comments — добавить комментарий (автоматически проверяется тональность)

GET /comments/{post_id} — список комментариев к посту

#### sentiment_service
POST /sentiment-check — анализ текста (text) на тональность (positive / negative)

## 5. 🧪 Тестирование
Сервисы включают изолированные тесты с in-memory базами и моками.
```bash
pytest --maxfail=1 --disable-warnings -v
```

## 6. 👨‍💻 Контакты и поддержка
Авторы: t.me/ramil2911, t.me/dedmokus
поддержки не будет
