from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import products
from app.core.config import settings
from app.middleware.security import SimpleRateLimitMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Product Agent System",
    description="Multi-agent system for product development using LangGraph",
    version="1.0.0"
)

app.add_middleware(SimpleRateLimitMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)

@app.get("/")
async def root():
    return {
        "message": "Product Agent System API",
        "version": "1.0.0",
        "agents": [
            "strategist",
            "market_researcher", 
            "prd_writer",
            "tech_architect",
            "ux_designer",
            "qa_engineer"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )