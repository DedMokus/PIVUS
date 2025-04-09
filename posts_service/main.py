import os
import uvicorn
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

app = FastAPI(title="Anonymous Posts Service")

DB_USER = os.getenv("POSTGRES_USER", "postgres_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres_password_123")
DB_NAME = os.getenv("POSTGRES_DB", "telegraph_db")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD, 
        host=DB_HOST,
        port=DB_PORT
    )

class PostCreate(BaseModel):
    title: str
    content: str

class Post(BaseModel):
    id: int
    title: str
    content: str
    edit_key: str

@app.post("/posts", response_model=Post)
def create_post(post_create: PostCreate):
    conn = get_connection()
    cur = conn.cursor()
    # Генерация ключа редактирования
    edit_key = "edit_key_" + str(abs(hash(post_create.title)))
    cur.execute(
        "INSERT INTO posts (title, content, edit_key) VALUES (%s, %s, %s) RETURNING id;",
        (post_create.title, post_create.content, edit_key)
    )
    post_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return Post(id=post_id, title=post_create.title, content=post_create.content, edit_key=edit_key)

@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, edit_key FROM posts WHERE id = %s;", (post_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return Post(id=row[0], title=row[1], content=row[2], edit_key=row[3])

@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: int, post_update: PostCreate, edit_key: str):
    conn = get_connection()
    cur = conn.cursor()
    # Проверяем ключ редактирования
    cur.execute("SELECT edit_key FROM posts WHERE id = %s;", (post_id,))
    stored_key = cur.fetchone()
    if not stored_key or stored_key[0] != edit_key:
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Invalid edit key")
    # Обновляем данные
    cur.execute(
        "UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING id, title, content, edit_key;",
        (post_update.title, post_update.content, post_id)
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return Post(id=updated[0], title=updated[1], content=updated[2], edit_key=updated[3])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
