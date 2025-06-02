from langchain_community.chat_models import ChatOpenAI
import os 
from langchain_google_genai import ChatGoogleGenerativeAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def llm_client():

    llm = ChatGoogleGenerativeAI(model= "gemini-1.5-flash", api_key = GOOGLE_API_KEY)
    return llm
