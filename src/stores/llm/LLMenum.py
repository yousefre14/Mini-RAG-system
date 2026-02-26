from enum import Enum

class LLMenum(Enum):

    OPENAI = "OPENAI"
    COHERE = "COHERE"

class OpenAiEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CohereEnum(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"
    DOCUMENT = "Search_document"
    QUERY = "Search_query"
    
class DocumentTypeEnum(Enum):
    DOCUMENT = "DOCUMENT"
    QUERY = "QUERY"
    