from .db_schemes import Asset
from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId


class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client)  # this will call the __init__ method
        return instance
    
    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        Asset.asset_id = result.inserted_id
        return Asset

    
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        records = await self.collection.find(
            {
                "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
                "asset_type": asset_type,
            }
        ).to_list(length=None)
    
        return [Asset(**record) for record in records] if records else []
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name
        })

        return Asset(**record) if record else None