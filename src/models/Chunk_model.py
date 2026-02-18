from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enumerates.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from motor.motor_asyncio import AsyncIOMotorClient


class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTIONS_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections= await self.db_client.collection_names()
        if DataBaseEnum.COLLECTIONS_CHUNK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTIONS_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])


    async def create_chunk(self, chunk: DataChunk = DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk_id = result.inserted_id
        return chunk
    
    async def get_chunks_by_chunk_id(self, chunk_id: str):
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        
        if result is None:
            return None
        
        return DataChunk(**result)
    
    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int = 100):
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            operations = [InsertOne(chunk.dict()) for chunk in batch]
            await self.collection.bulk_write(operations)

        return len(chunks)