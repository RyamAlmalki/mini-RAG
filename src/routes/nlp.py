from fastapi import APIRouter, Depends, UploadFile, status, Request
from helper.config import Settings, get_settings
from fastapi.responses import JSONResponse
import logging
from .schemas.nlp import PushRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from models import ResponseSignal

logger = logging.getLogger('uvicorn.error')

router = APIRouter()


@router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):

    # This will handle the talking with mongo db project collection
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    # This will handle the talking with mongo db chunk collection
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )

    # this will get the Project model
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    # This will handle the NLP operations like indexing into vector db
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )
    
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_number=page_no)
        
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        # page_chunks = ['chunk1', 'chunk2', 'chunk3']
        # len(page_chunks) = 3
        # range(1, 1 + 3) = range(1, 4) -> [1, 2, 3]
        chunks_ids =  list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = await nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunks_ids
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                }
            )
        
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERTION_INTO_VECTOR_DB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )


@router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    # This will handle the talking with mongo db project collection
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )


    # this will get the Project model
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # This will handle the NLP operations like indexing into vector db
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )

    collection_info = await nlp_controller.get_vector_db_collection_info(
        project=project
    )

    if not collection_info:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.COLLECTION_NOT_FOUND_ERROR.value
            }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTOR_DB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )