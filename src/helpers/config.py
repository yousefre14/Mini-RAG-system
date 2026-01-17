from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    openai_API_KEY: str
    File_ALLOWED_Types: list
    File_MAX_SIZE: int = 10485760
    FILE_DEFAULT_CHUNK_SIZE: int = 512000


    class Config:
        env_file = ".env"

def get_settings():
    return Settings()