import os 
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def llm_client():

    """Initializes and returns a chat model client based on available API keys.

    Returns: 
    -BaseChatModel : An instance of ChatOpenAI or ChatGoogleGenerativeAI.
 
    """

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    if OPENAI_API_KEY:
        return ChatOpenAI(model= "gpt-4o", api_key = OPENAI_API_KEY)
        
    elif GOOGLE_API_KEY:
        return ChatGoogleGenerativeAI(model = "gemini-2.0-flash", api_key = GOOGLE_API_KEY)
    
    else:
        raise EnvironmentError("No API keys fouund. Set OPENAI_API_KEY or GOOGLE_API_KEY ")
    
