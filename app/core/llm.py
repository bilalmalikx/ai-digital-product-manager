from langchain_open import ChatOpenAI
from langsmith import tracing_v2_enabled
from app.core.settings import settings

def get_llm():
    """Get the language model instance."""
    if tracing_v2_enabled():
        print("Tracing v2 is enabled. Using LangSmith for tracing.")
    else:
        print("Tracing v2 is not enabled. Using default tracing.")

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        openai_api_key=settings.OPENAI_API_KEY,
    )
    return llm