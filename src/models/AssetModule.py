from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enumerates.DataBaseEnum import DataBaseEnum
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client=db_client)
        self.collection = None

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        """Initialize the MongoDB collection and indexes."""
        if self.collection is not None:
            return

        db = self.db_client  # db_client should be a database instance
        self.collection = db[DataBaseEnum.COLLECTION_ASSET_NAME.value]

        # create indexes if collection is new
        existing_collections = await db.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in existing_collections:
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_asset(self, asset: Asset):
        if self.collection is None:
            await self.init_collection()

        # Convert project_id to string if needed
        asset_dict = asset.dict(exclude_unset=True)
        if "asset_project_id" in asset_dict and isinstance(asset_dict["asset_project_id"], str):
            asset_dict["asset_project_id"] = str(asset_dict["asset_project_id"])

        result = await self.collection.insert_one(asset_dict)
        asset.asset_id = str(result.inserted_id)
        return asset

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        """Return all assets for a project as Pydantic Asset objects."""
        if self.collection is None:
            await self.init_collection()

        query = {
            "asset_project_id": str(asset_project_id),
            "asset_type": asset_type
        }
        cursor = self.collection.find(query)
        assets = []
        async for document in cursor:
            # Convert MongoDB _id to asset_id for consistency
            document["asset_id"] = str(document.get("_id", ""))
            assets.append(Asset(**document))
        return assets
