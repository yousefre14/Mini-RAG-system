from .LLMenum import LLMenum
from .providers.OpenAiProvider import OpenAiProvider
from .providers.CohereProvider import CohereProvider

class LLMProviderFactory:
    def __init__(self , config : dict):
        self.config = config

    def create(self, provider : str):
        if provider == LLMenum.OPENAI.value:
            return OpenAiProvider(
                api_key = self.config.get("OPENAI_API_KEY"),
                api_url = self.config.get("OPENAI_API_URL"),
                default_input_max_characters = self.config.get("DEFAULT_INPUT_MAX_CHARACTERS", 1000),
                default_output_max_charcters = self.config.get("DEFAULT_OUTPUT_MAX_CHARCTERS", 1000),
                default_generation_temprature = self.config.get("DEFAULT_GENERATION_TEMPRATURE", 0.1)
            )
        
        if provider == LLMenum.COHERE.value:
            return CohereProvider(
                api_key = self.config.get("COHERE_API_KEY"),
                default_input_max_characters = self.config.get("DEFAULT_INPUT_MAX_CHARACTERS", 1000),
                default_output_max_charcters = self.config.get("DEFAULT_OUTPUT_MAX_CHARCTERS", 1000),
                default_generation_temprature = self.config.get("DEFAULT_GENERATION_TEMPRATURE", 0.1)
            )
         
        return None