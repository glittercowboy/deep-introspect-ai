"""
DeepIntrospect AI - Backend API
"""
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import chat, auth, users, insights, health
from app.core.logging import configure_logging
from app.core.exceptions import setup_exception_handlers

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A groundbreaking self-reflection AI chatbot API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}", tags=["Users"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}", tags=["Chat"])
app.include_router(insights.router, prefix=f"{settings.API_V1_STR}", tags=["Insights"])
app.include_router(health.router, prefix=f"{settings.API_V1_STR}", tags=["Health"])

@app.on_event("startup")
async def startup_event():
    """Execute startup tasks"""
    logger.info("Starting DeepIntrospect AI API")
    # Initialize connections and services
    
@app.on_event("shutdown")
async def shutdown_event():
    """Execute shutdown tasks"""
    logger.info("Shutting down DeepIntrospect AI API")
    # Clean up connections and resources

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)