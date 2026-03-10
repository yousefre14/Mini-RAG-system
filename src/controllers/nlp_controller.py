from .BaseController import BaseController
from src.models.db_schemas import Project , DataChunk
from typing import List
from src.stores.llm.LLMenum import DocumentTypeEnum
import os
import json

class NLPController(BaseController):
    def __init__(self, vectordb_client, generation_client, embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client= generation_client
        self.embedding_client = embedding_client

    def create_collection_name(self , project_id : str):
        return f"collection_{project_id}".strip()
    
    def reset_dbcollection(self, project: Project):
        collection_name = self.create_collection_name(project_id= project.project_id)
        return self.vectordb_client.delet_collection(collection_name= collection_name)

    def get_vector_db_collection_info (self, project:Project):
        collection_name = self.create_collection_name(project_id= project.project_id)
        collection_info = self.vectordb_client.get_collection_info( collection_name = collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_info_vectordb(self, project:Project, chunks: List[DataChunk],
                            chunk_ids : List [int],
                            do_reset : bool = False): 

    #step 1 get collection name 
        collection_name = self.create_collection_name(project_id= project.project_id)

    #step 2 manage items 
        texts = [c.chunk_text for c in chunks ]
        metadata = [ c.chunk_metadata for c in chunks]
        vectors = [self. embedding_client.embed_text (text =texts, document_type = DocumentTypeEnum.DOCUMENT.value)
                   for text in texts]

    #step 3 create collection if not exist 

        _= self.vectordb_client.create_collection (collection_name= collection_name, do_reset= do_reset, embedding_size = self.embedding_client.embedding_size)
    # step 4 insert into vector db
        _= self.vectordb_client.insert_many(
            collection_name= collection_name,
            list_of_texts=texts,
            metadatas= metadata,
            list_of_vectors= vectors,
            record_ids = chunk_ids
        )
        return True
    
    def search_vector_db_collection(self,project:Project,text:str,limit:int =10):
        #step 1 get collection name 
        collection_name = self.create_collection_name(project_id= project.project_id)
        #step 2 get text embedding vector
        vector = self.embedding_client.embed_text(
            text = text , document_type = DocumentTypeEnum.QUERY.value
        )

        if not vector or len (vector) == 0:
            return False
        
        #step 3 do semantic search 
        results = self.vectordb_client.search_by_vector(collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False
        
        return json.loads(
            json.dumps(results
                       , default=lambda x: x.__dict__)
        )
