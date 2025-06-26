import os
from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helper.config import Settings, get_settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseSignal
from .schemas.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunks
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import Assets
from models.enums.AssetTypeEnum import AssetTypeEnum
from controllers import NLPController

router = APIRouter()

@router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: int, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client,
    )

    project_db = await project_model.get_project_or_create_one(project_id=project_id)
    
    if project_db is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Project not found or could not be created."}
        )
    

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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": ResponseSignal.FILE_UPLOAD_FAILED.value} 
        )

    # Store the asset into the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client,
    )
    asset = Assets(
        asset_project_id=project_db.project_id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
    )

    asset_record = await asset_model.create_asset(asset=asset)
    
    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": ResponseSignal.FILE_UPLOAD_FAILED.value}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": result_signal,
            "file_id": str(asset_record.asset_id),
        }
    )


@router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: int, process_request: ProcessRequest):
    
    
    chunk_size = process_request.chunk_size
    chunk_overlap = process_request.chunk_overlap
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client,
    )

    project_db = await project_model.get_project_or_create_one(project_id=project_id)
    

    nlp_controller = NLPController(
        vector_db_client = request.app.vector_db_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,
    )

    
    # Store the asset into the database
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client,
    )

    project_files_ids = {}

    if process_request.file_id is not None:
        
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project_db.project_id,
            asset_name=process_request.file_id
        )
        
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": ResponseSignal.FILE_ID_ERROR.value}
            )
        else:
            project_files_ids = {
                asset_record.asset_project_id: asset_record.asset_name
            }
    else:

        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project_db.project_id,
            asset_type=AssetTypeEnum.FILE.value
        )

        project_files_ids = {
            asset_record.asset_id : asset_record.asset_name
            for asset_record in project_files
        }
    

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": ResponseSignal.NO_FILES_FOUND.value}
        )
    

    process_controller = ProcessController(project_id=project_id)

    number_of_records = 0
    number_of_files = 0

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client,
    )

    if do_reset == 1:
        # delete associated vectors collection
        collection_name = nlp_controller.create_collection_name(project_id=project_db.project_id)
        _ = await nlp_controller.vector_db_client.delete_collection(collection_name=collection_name)

        # delete associated chunks
        _ = await chunk_model.delete_chunk_by_project_id(project_id=project_db.project_id)
    
    for asset_id, file_id in project_files_ids.items():
        
        file_contents = process_controller.get_file_content(file_id=file_id)

        file_chunks = process_controller.process_file_content(
            file_contents=file_contents,
            file_id=file_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        if file_chunks is None:
            continue

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": ResponseSignal.PROCESSING_FAILED.value}
            )
        
        file_chunks_records = [
            DataChunks(
                chunk_project_id=project_db.project_id,
                chunk_asset_id=asset_id,
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1
            )
            for i, chunk in enumerate(file_chunks)
        ]
        
        number_of_records += await chunk_model.insert_many_chunks(
            chunks=file_chunks_records,
            batch_size=100
        )

        number_of_files += 1

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": number_of_records,
            "processed_files": number_of_files
        }
    )
    

