from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enumerates.DataBaseEnum import DataBaseEnum
from motor.motor_asyncio import AsyncIOMotorClient

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.PROJECTS.value]


    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        all_collections= await self.db_client.list_collection_names()
        if DataBaseEnum.PROJECTS.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.PROJECTS.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_project(self, project: Project = Project):
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        return result.inserted_id
    async def get_project_or_createone(self, project_id: str):
        record = await self.collection.find_one({"project_id": project_id})
        
        if record is None:
            # If the project does not exist, create a new one
            new_project = Project(project_id=project_id)
            new_project = await self.create_project(new_project)
            return new_project
        
        return Project(**record)
    
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        # count total number of documents
        total_documents = await self.collection.count_documents({})
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip((page-1) * page_size).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        return projects, total_pages