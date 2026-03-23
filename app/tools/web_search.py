from typing import Optional
import aiohttp
import json
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def web_search_tool(query: str, num_results: int = 5) -> Optional[dict]:
    """Web search tool using Tavily or SerpAPI."""
    
    try:
        if settings.TAVILY_API_KEY:
            return await tavily_search(query, num_results)
        elif settings.SERPAPI_API_KEY:
            return await serpapi_search(query, num_results)
        else:
            logger.warning("No search API key configured")
            return None
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return None

async def tavily_search(query: str, num_results: int) -> dict:
    """Search using Tavily API."""
    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.TAVILY_API_KEY}"
    }
    payload = {
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": num_results
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await response.json()

async def serpapi_search(query: str, num_results: int) -> dict:
    """Search using SerpAPI."""
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": settings.SERPAPI_API_KEY,
        "num": num_results
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()