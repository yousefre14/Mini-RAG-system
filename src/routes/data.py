from fastapi import APIRouter, Depends, UploadFile, status
import os
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
import aiofiles
from models.enumerates.responseEnamurates import ResponseSignals
import logging

logger = logging.getLogger("uvicor_errors")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):

    # Validate file properties
    is_valid, result_signal = DataController().validate_uploaded_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
        )
    
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
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
        content={
            "signal": ResponseSignals.SUCCESS.value,
            "message": f"File '{file.filename}' uploaded successfully to project '{project_id}'."
        }
    )
