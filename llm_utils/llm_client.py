import os 
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel

def llm_client()-> BaseChatModel:

    """Initializes and returns a chat model client based on available API keys.

    Returns: 
    BaseChatModel: A chat model instance, either 'ChatOpenAI' or 'ChatGoogleGenerativeAI', depending on the available API key.

    Raises:
    EnvironmentError: If neither 'OPENAI_API_KEY' nor 'GOOGLE_API_KEY'is set in the environment.
 
    """

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    if OPENAI_API_KEY:
        return ChatOpenAI(model= "gpt-4o", api_key = OPENAI_API_KEY)
        
    elif GOOGLE_API_KEY:
        return ChatGoogleGenerativeAI(model = "gemini-2.0-flash", api_key = GOOGLE_API_KEY)
    
    else:
        raise EnvironmentError("No API keys fouund. Set OPENAI_API_KEY or GOOGLE_API_KEY ")
    
