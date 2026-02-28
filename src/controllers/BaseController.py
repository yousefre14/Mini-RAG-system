from src.helpers.config import get_settings, Settings
import os

class BaseController:

    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir= os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(self.base_dir, 
                                     "assets/files")
        self.vector_db_dir = os.path.join(self.base_dir,
                                            "assets/vectordb")  # Directory for vector database files
        
    def get_vector_db_provider(self, db_name: str ):
        database_path = os.path.join(self.vector_db_dir, 
                                     db_name)
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return database_path