from tortoise.models import Model
from tortoise import fields
import uuid

class BlogPost(Model):
    id = fields.IntField(pk=True)
    key = fields.UUIDField(default=uuid.uuid4, unique=True)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)