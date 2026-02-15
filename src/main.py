from fastapi import FastAPI
from src.routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import Settings, get_settings

app = FastAPI()
@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()

    app.mongo_conn= AsyncIOMotorClient(settings.MongoDB_URI)
    app.db_client = app.mongo_conn[settings.MongoDB_DATABASE]
    
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)

