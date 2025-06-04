from fastapi import APIRouter, Depends
from helper.config import Settings, get_settings

router = APIRouter()

@router.get("/")
async def root(app_settings: Settings = Depends(get_settings)):
    return {"app name": app_settings.APP_NAME}
