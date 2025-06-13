from .db_schemes import Assets
from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy import select, delete

class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client)  # this will call the __init__ method
        return instance
    
    async def create_asset(self, asset: Assets):
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
        
        return asset

    
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        async with self.db_client() as session:
            stmt = select(Assets).where(
                Assets.asset_project_id == asset_project_id,
                Assets.asset_type == asset_type
            )
        
            result = await session.execute(stmt)
            assets = result.scalars().all()
        return assets
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
       
        async with self.db_client() as session:
            stmt = select(Assets).where(
                Assets.asset_project_id == asset_project_id,
                Assets.asset_name == asset_name
            )
        
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()

        return record
