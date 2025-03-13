from tortoise import Tortoise

async def init_db():
    await Tortoise.init(
        db_url='postgres://postgres:postgres@db:5432/microblog',
        modules={'models': ['app.models']}
    )
    await Tortoise.generate_schemas()

async def get_db():
    return Tortoise.get_connection("default")