"""
Professional AI Resume Analyzer - FastAPI Backend
Handles resume uploads, PDF extraction, and skill matching analysis
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routes and database
from backend.database import init_db
from backend.routes import analyze, history, compare

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("=" * 60)
    logger.info("Starting AI Resume Analyzer API")
    logger.info("=" * 60)
    try:
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown event
    logger.info("=" * 60)
    logger.info("Shutting down AI Resume Analyzer API")
    logger.info("=" * 60)

# Create FastAPI application
app = FastAPI(
    title="AI Resume Analyzer API",
    description="Professional resume analysis using AI-powered skill matching",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS configuration for development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected error occurred. Please try again.",
            "timestamp": datetime.now().isoformat()
        }
    )

# Include API routers
logger.info("Registering API routes...")
app.include_router(analyze.router, tags=["Analysis"])
app.include_router(history.router, tags=["History"])
app.include_router(compare.router, tags=["Comparison"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "AI Resume Analyzer",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

# API status endpoint
@app.get("/api/status")
async def api_status():
    """Get API status and available endpoints"""
    return {
        "status": "operational",
        "service": "AI Resume Analyzer API",
        "version": "2.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "history": "/api/history",
            "compare": "/api/compare",
            "documentation": "/api/docs"
        },
        "timestamp": datetime.now().isoformat()
    }

# Mount frontend static files
logger.info("Mounting frontend assets...")
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server on 0.0.0.0:8000")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
