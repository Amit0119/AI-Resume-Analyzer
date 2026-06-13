"""
WSGI entry point for production deployment on Render
"""
from backend.main import app

# This is the entry point for Render/Gunicorn
# Render will run: gunicorn app:app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # Never reload in production
    )