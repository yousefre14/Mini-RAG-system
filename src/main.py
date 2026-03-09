from fastapi import FastAPI
from src.routes import base, nlp, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import Settings, get_settings
from src.stores.llm.LLMProviderFactory import LLMProviderFactory
from src.stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()

    app.mongo_conn= AsyncIOMotorClient(settings.MongoDB_URI)
    app.db_client = app.mongo_conn[settings.MongoDB_DATABASE]

    llm_factory = LLMProviderFactory(config=settings.dict())
    vectordb_provider_factory = VectorDBProviderFactory(config=settings.dict())

    # generation client
    app.generation_client = llm_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    # vector database client
    app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()
    app.vectordb_client.set_vector_db_model(model_id=settings.VECTOR_DB_MODEL_ID)

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()
    app.vectordb_client.disconnect()

app.include_router(base.base_router)        # make sure base_router exists in base.py
app.include_router(data.data_router)        # must match exactly `data_router` in data.py
app.include_router(nlp.nlp_router)

