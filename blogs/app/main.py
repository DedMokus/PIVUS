from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime
from .database import get_db, init_db
from .models import BlogPost
from tortoise.exceptions import DoesNotExist

app = FastAPI()


class BlogCreate(BaseModel):
    content: str


class BlogUpdate(BaseModel):
    content: str


@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/blogs", status_code=201)
async def create_blog(blog_data: BlogCreate):
    blog = await BlogPost.create(
        content=blog_data.content,
        key=uuid4()
    )
    return {"key": str(blog.key)}


@app.get("/blogs/{key}")
async def read_blog(key: str):
    try:
        uuid_key = UUID(key)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid key format")

    blog = await BlogPost.get_or_none(key=uuid_key)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"content": blog.content}


@app.put("/blogs/{key}")
async def update_blog(key: str, blog_data: BlogUpdate):
    try:
        uuid_key = UUID(key)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid key format")

    blog = await BlogPost.get_or_none(key=uuid_key)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    blog.content = blog_data.content
    blog.updated_at = datetime.utcnow()
    await blog.save()
    return {"message": "Blog updated successfully"}