from .BaseController import BaseController
from fastapi import UploadFile
from src.models.enumerates.responseEnamurates import ResponseSignals
class DataController(BaseController):

    def __init__(self):
        super().__init__()

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.File_ALLOWED_Types:
            return False, ResponseSignals.INVALID_FILE_TYPE.value
        if file.size > self.app_settings.File_MAX_SIZE:
            return False, ResponseSignals.FILE_TOO_LARGE.value
        
        return True, ResponseSignals.SUCCESS.value

