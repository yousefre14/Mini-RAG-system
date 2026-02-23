from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime


class Asset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    asset_id: str = Field(..., min_length=1)
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)

    asset_size: Optional[int] = Field(default=None, gt=0)
    asset_config: Optional[int] = Field(default=None, gt=0)

    asset_pushed_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("asset_id", 1)],
                "name": "asset_id_index_1",
                "unique": True,
            }
        ]
