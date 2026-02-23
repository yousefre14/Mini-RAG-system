from fastapi import APIRouter, Depends, UploadFile, status, Request
import os
import logging
import aiofiles
from pydantic import BaseModel

from fastapi.responses import JSONResponse
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController, ProcessController
from src.models.enumerates.responseEnamurates import ResponseSignals
from src.routes.schemas.data import processRequest
from src.models.ProjectModel import ProjectModel
from src.models.Chunk_model import ChunkModel
from src.models.db_schemas import DataChunk
from src.models.AssetModule import AssetModel
from src.models.db_schemas import Asset
from src.models.enumerates.AsserTypeEnum import AssetTypeEnum
import uuid

logger = logging.getLogger("uvicorn_errors")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,  # make sure project_id is always a string
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    # get or create project
    project_model = await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_createone(project_id)

    # validate file
    is_valid, result_signal = DataController().validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
        )

    # save file to project directory
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

    # store asset in DB
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    asset_resource = Asset(
        asset_id=str(uuid.uuid4()),
        asset_project_id=str(project.project_id),
        asset_type=AssetTypeEnum.file.value,
        asset_name=file.filename,
        asset_size=os.path.getsize(saved_file_path)
    )
    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.SUCCESS.value,
            "message": f"File '{file.filename}' uploaded successfully to project '{project_id}'.",
            "file_id": str(asset_record.asset_id),  # use actual asset_id
            "project_id": str(project_id)
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request,
    project_id: str,  # keep project_id as string
    process_request: processRequest
):
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    # get project
    project_model = await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_createone(project_id=project_id)

    # determine which files to process
    project_file_ids = []
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    if process_request.file_id:
        # single file
        project_file_ids = [process_request.file_id]
    else:
        # all files for this project
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project_id,
            asset_type=AssetTypeEnum.file.value
        )
        project_file_ids = [record.asset_id for record in project_files]  # use asset_id

    if not project_file_ids:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No files found for the specified project."}
        )

    process_controller = ProcessController(project_id=project_id)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    no_records_inserted = 0
    no_files_processed = 0

    if process_request.do_reset:
        await chunk_model.delete_chunks_by_project_id(project_id=project._id)

    for file_id in project_file_ids:
        file_content = process_controller.get_file_content(file_id=file_id)
        if not file_content:
            logger.error(f"Failed to load content for file_id: {file_id} in project_id: {project_id}")
            continue

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            chunk_overlap=overlap_size
        )

        if not file_chunks:
            logger.warning(f"No chunks generated for file_id: {file_id}")
            continue

        # prepare DB records
        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project._id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        inserted = await chunk_model.insert_many_chunks(chunks=file_chunks_records)
        no_records_inserted += inserted
        no_files_processed += 1

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.SUCCESS.value,
            "message": f"{no_records_inserted} chunks inserted successfully.",
            "project_id": str(project_id),
            "processed_files": no_files_processed
        }
    )
