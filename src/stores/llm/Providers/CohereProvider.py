from ..LLMinterface import LLminterface
from ..LLMenum import CohereEnum , DocumentTypeEnum
import cohere
import logging
from typing import List, Union


class CohereProvider(LLminterface):
    def __init__ (self, api_key : str ,
                  default_input_max_characters : int = 1000,
                  default_output_max_charcters : int =1000,
                  default_generation_temprature : float =0.1):
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_charcters = default_output_max_charcters
        self.default_generation_temprature = default_generation_temprature
        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)
        self.enums = CohereEnum

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id : str):
        self.generation_model_id= model_id

    def set_embedding_model(self, model_id :str, embedding_size : int):
        self.embedding_model_id = model_id
        self.embedding_size= embedding_size

    def process_text(self, text):
        if isinstance(text, list):
             text = " ".join(text)

        return text[:self.default_input_max_characters].strip()
    
    def generate_text (self , prompt : str , chat_history: list = [], max_output_token: int=None,
                        temperature : float = None):
        if not self.client:
            self.logger.warning("OpenAi client wasn't set")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model wasn't set")
            return None
        
        max_output_token = max_output_token if max_output_token else self.default_output_max_charcters
        temperature = temperature if temperature else self.default_generation_temprature

        
        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message= self.process_text(prompt),
            max_tokens=max_output_token,
            temperature=temperature
        )
        if not response or not response.text or not response.text[0]:
            self.logger.error("error while generating text")
            return None
        return response.text[0]
    
    def embed_text (self , text : str , document_type : str = None):
        if not self.client:
            self.logger.warning("OpenAi client wasn't set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model wasn't set")
            return None
        input_type = CohereEnum.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CohereEnum.QUERY

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type.value,
            embedding_types=["float"],
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("error while embedding text")
            return None
        return response.embeddings.float[0]
    

    def construct_prompt (self, prompt :str , role :str):
        return {"role": role, 
                "text": self.process_text(prompt)}
