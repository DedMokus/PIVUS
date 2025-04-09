import os
import uvicorn
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import requests

app = FastAPI(title="Anonymous Comments Service")

DB_USER = os.getenv("POSTGRES_USER", "postgres_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres_password_123")
DB_NAME = os.getenv("POSTGRES_DB", "telegraph_db")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

SENTIMENT_HOST = os.getenv("SENTIMENT_HOST", "sentiment_service")
SENTIMENT_PORT = os.getenv("SENTIMENT_PORT", "8003")

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD, 
        host=DB_HOST,
        port=DB_PORT
    )

class CommentCreate(BaseModel):
    post_id: int
    content: str

class Comment(BaseModel):
    id: int
    post_id: int
    content: str
    is_approved: bool

@app.post("/comments", response_model=Comment)
def create_comment(comment_create: CommentCreate):
    # Запрос к sentiment_service для проверки тональности
    sentiment_url = f"http://{SENTIMENT_HOST}:{SENTIMENT_PORT}/sentiment-check"
    resp = requests.post(sentiment_url, json={"text": comment_create.content})
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Sentiment service error")
    
    sentiment_result = resp.json().get("sentiment", "negative")
    is_approved = sentiment_result != "negative"  # Пример супер-простого правила
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments (post_id, content, is_approved) VALUES (%s, %s, %s) RETURNING id;",
        (comment_create.post_id, comment_create.content, is_approved)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return Comment(id=new_id, post_id=comment_create.post_id, content=comment_create.content, is_approved=is_approved)

@app.get("/comments/{post_id}", response_model=List[Comment])
def list_comments(post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, post_id, content, is_approved FROM comments WHERE post_id = %s;", (post_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    comments = []
    for row in rows:
        comment = Comment(id=row[0], post_id=row[1], content=row[2], is_approved=row[3])
        comments.append(comment)
    return comments

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
