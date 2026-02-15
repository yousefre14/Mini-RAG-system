from fastapi import APIRouter, Depends, UploadFile, status, Request
import os
import logging
import aiofiles

from fastapi.responses import JSONResponse
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController, ProcessController
from src.models.enumerates.responseEnamurates import ResponseSignals
from src.routes.schemas.data import processRequest
from src.models.ProjectModel import ProjectModel
from src.models.Chunk_model import ChunkModel
from src.models.db_schemas import DataChunk

logger = logging.getLogger("uvicorn_errors")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    project_model = ProjectModel(request.app.db_client)
    project = await project_model.get_project_or_createone(project_id=project_id)

    # Validate file
    is_valid, result_signal = DataController().validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
        )

    # Save file to project directory
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    os.makedirs(project_dir_path, exist_ok=True)
    saved_file_path = os.path.join(project_dir_path, file.filename)

    try:
        async with aiofiles.open(saved_file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An error occurred while uploading the file."}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.SUCCESS.value,
            "message": f"File '{file.filename}' uploaded successfully to project '{project_id}'.",
            "file_id": str(project_id),
            "project_id": str(project_id)
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request,
    project_id: str,
    process_request: processRequest
):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    project_model = ProjectModel(request.app.db_client)
    project = await project_model.get_project_or_createone(project_id=project_id)

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        chunk_overlap=overlap_size
    )

    if not file_chunks:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Failed to process the file content."}
        )

    # Prepare DB records
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project._id
        )
        for i, chunk in enumerate(file_chunks)
    ]

    # Insert chunks into DB
    chunk_model = Chunk_model(db_client=request.app.db_client)
    no_records_inserted = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.SUCCESS.value,
            "message": f"{no_records_inserted} chunks inserted successfully.",
            "project_id": str(project_id),
            "file_id": str(file_id)
        }
    )
