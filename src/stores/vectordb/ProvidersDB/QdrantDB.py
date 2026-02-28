from ..VectorDBinterface import VectorDBInterface
import logging
from ..VectorDBEnum import DistaceMethodeEnum
from qdrant_client import QdrantClient , models
from typing import List

class QdrantDB(VectorDBInterface):
    def __init__(self, db_path: str , distance_method: DistaceMethodeEnum):
        self.db_path = db_path
        self.client= None
        self.distance_method = None
        if distance_method == DistaceMethodeEnum.Cosine:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistaceMethodeEnum.Euclidean:
            self.distance_method = models.Distance.Euclidean
        elif distance_method == DistaceMethodeEnum.DotProduct:
            self.distance_method = models.Distance.DotProduct

        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info(f"Connected to QdrantDB at {self.db_path}")

    def disconnect(self):
        self.client = None
        self.logger.info("Disconnected from QdrantDB")

    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> list:
        return self.client.get_collections().collections
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name).dict()
    
    def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        self.logger.info(f"Collection {collection_name} deleted successfully")

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset :
            self.delete_collection(collection_name)
        if not self.is_collection_exists(collection_name):
            self.client.create_collection(collection_name=collection_name, 
                                          vectors_config=models.VectorParams(size=embedding_size, 
                                                                             distance=self.distance_method))
            return True
        return False
    
    def insert_one(self, collection_name: str, text: str, 
                   vector: list, metadata: dict = None, record_id: str = None):
        if not self.is_collection_exists(collection_name):
                self.logger.error(f"Collection {collection_name} does not exist")
                return False
        
        try:
            _= self.client.upload_records(collection_name=collection_name, records= [ models.Record(id=record_id, vector=vector, payload={"text": text, **(metadata or {})})])
        except Exception as e:
            self.logger.error(f"Error uploading record to QdrantDB: {e}")
        return True
    

    def insert_many(self, collection_name: str, list_of_texts: list,
                     list_of_vectors: list, metadatas:  list = None, 
                     record_ids: list = None, batch_size: int =50):    
        if metadatas is None:
            metadatas = [None] * len(list_of_texts)
        if record_ids is None:
            record_ids = [None] * len(list_of_texts)

        for i in range (0 , len(list_of_texts), batch_size):
            batch_end = i + batch_size
            batch_texts = list_of_texts[i:batch_end]
            batch_vectors = list_of_vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]
            batch_records = [
                models.Record(id=batch_record_ids[x], vector=batch_vectors[x], payload={"text": batch_texts[x], **(batch_metadatas[x] or {})})
                for x in range(len(batch_texts))
            ]
            try:
                _= self.client.upload_records(collection_name=collection_name, records=batch_records)
            except Exception as e:
                self.logger.error(f"Error uploading records to QdrantDB: {e}")
                return False

        return True    
    
    def search_by_vector(self,collection_name: str, vector: list, limit: int= 5):
        return self.client.search(collection_name=collection_name, 
                                  query_vector=vector, limit=limit)
