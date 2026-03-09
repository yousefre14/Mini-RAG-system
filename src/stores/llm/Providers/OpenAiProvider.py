from ..LLMinterface import LLminterface
from openai import OpenAI
import logging
from ..LLMenum import OpenAiEnum

class OpenAiProvider(LLminterface):
    def __init__ (self, api_key : str , api_url : str=None ,
                  default_input_max_characters : int = 1000,
                  default_output_max_charcters : int =1000,
                  default_generation_temprature : float =0.1):
         self.api_key = api_key
         self.api_url = api_url
         self.default_input_max_characters = default_input_max_characters
         self.default_output_max_charcters = default_output_max_charcters
         self.default_generation_temprature = default_generation_temprature
         self.generation_model_id = None

         self.embedding_model_id = None
         self.embedding_size = None

         self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.api_url
         )

         self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id : str):
        self.generation_model_id= model_id

    def set_embedding_model(self, model_id :str, embedding_size : int):
        self.embedding_model_id = model_id
        self.embedding_size= embedding_size

    def process_text(self, text :str):
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

        chat_history.append(self.construct_prompt(prompt= prompt, role= OpenAiEnum.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_token,
            temperature=temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("error while generating text")
            return None
        return response.choices[0].message.content
    


    def embed_text (self , text : str , document_type : str = None):
        if not self.client:
            self.logger.warning("OpenAi client wasn't set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model wasn't set")
            return None

        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text,

        )

        if not response or not response.data or len(response.data)== 0 or not response.data[0].embedding:
            self.logger.error("error while embedding text")
            return None
        return response.data[0].embedding
    
    def construct_prompt (self, prompt :str , role :str):
        return {"role": role, 
                "content": self.process_text(prompt)}
