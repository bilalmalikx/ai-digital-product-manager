from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models import BaseChatModel
from langsmith import traceable
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_llm(model_name: str = None, temperature: float = 0.7) -> BaseChatModel:
    """Get the language model instance based on configuration."""
    
    model = model_name or settings.DEFAULT_MODEL
    
    try:
        if settings.MODEL_PROVIDER == "openai":
            llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=settings.OPENAI_API_KEY,
                max_tokens=4000
            )
        elif settings.MODEL_PROVIDER == "anthropic":
            llm = ChatAnthropic(
                model=model,
                temperature=temperature,
                api_key=settings.ANTHROPIC_API_KEY,
                max_tokens=4000
            )
        elif settings.MODEL_PROVIDER == "deepseek":
            llm = ChatDeepSeek(
                model=model,
                temperature=temperature,
                api_key=settings.DEEPSEEK_API_KEY,
                max_tokens=4000
            )
        else:
            raise ValueError(f"Unsupported model provider: {settings.MODEL_PROVIDER}")
        
        logger.info(f"Initialized LLM: {settings.MODEL_PROVIDER}/{model}")
        return llm
        
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise

@traceable(name="llm_invoke")
def invoke_llm_with_tracing(llm: BaseChatModel, prompt: str) -> str:
    """Invoke LLM with LangSmith tracing."""
    response = llm.invoke(prompt)
    return response.content