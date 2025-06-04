from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helper.config import Settings, get_settings
from controllers import DataController, ProjectController
import aiofiles
from models import ResponseSignal
import logging 

logger = logging.getLogger('uvicorn.error')

router = APIRouter()

@router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
    )

    file_path, file_id = data_controller.generate_unique_filepath(
        original_file_name=file.filename,
        project_id=project_id
    )

    try: 
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": ResponseSignal.FILE_UPLOAD_FAILED.value} 
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": result_signal,
            "file_path": file_path,
            "file_id": file_id,
        }
    )
