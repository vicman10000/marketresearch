"""
Market Research Visualization - FastAPI Server
Main application entry point with static file serving and API routes
"""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import structlog

from server.config import settings
from server.api import market_data, analytics
from server.auth import routes as auth_routes
from server.websocket import routes as ws_routes
from server.database import init_db

# Setup logging
logger = structlog.get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
app.include_router(auth_routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(market_data.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_routes.router, prefix=settings.API_V1_PREFIX)

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / settings.OUTPUTS_DIR


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("server_starting", 
                host=settings.HOST, 
                port=settings.PORT,
                outputs_dir=str(OUTPUTS_DIR))
    
    # Initialize database
    try:
        init_db()
        logger.info("database_tables_initialized")
    except Exception as e:
        logger.error("database_initialization_error", error=str(e))
    
    # Ensure outputs directory exists
    if not OUTPUTS_DIR.exists():
        logger.warning("outputs_directory_not_found", 
                      path=str(OUTPUTS_DIR),
                      action="creating")
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("server_shutting_down")


@app.get("/", response_class=FileResponse)
async def read_root():
    """Serve the main dashboard page"""
    index_path = OUTPUTS_DIR / "index.html"
    
    if not index_path.exists():
        logger.error("index_not_found", path=str(index_path))
        raise HTTPException(
            status_code=404, 
            detail="Dashboard not generated yet. Please run 'python app.py' first to generate visualizations."
        )
    
    return FileResponse(index_path)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "version": settings.API_VERSION,
        "outputs_available": OUTPUTS_DIR.exists()
    })


@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    # Check for available visualizations
    static_dir = OUTPUTS_DIR / "static"
    animated_dir = OUTPUTS_DIR / "animated"
    
    visualizations = {
        "static": [],
        "animated": []
    }
    
    if static_dir.exists():
        visualizations["static"] = [f.name for f in static_dir.glob("*.html")]
    
    if animated_dir.exists():
        visualizations["animated"] = [f.name for f in animated_dir.glob("*.html")]
    
    # Check for metadata
    metadata_path = OUTPUTS_DIR / "metadata.json"
    has_metadata = metadata_path.exists()
    
    # Check for report
    report_path = OUTPUTS_DIR / "market_report.txt"
    has_report = report_path.exists()
    
    return JSONResponse({
        "status": "operational",
        "version": settings.API_VERSION,
        "outputs_directory": str(OUTPUTS_DIR),
        "visualizations": visualizations,
        "has_metadata": has_metadata,
        "has_report": has_report,
        "total_visualizations": len(visualizations["static"]) + len(visualizations["animated"])
    })


# Mount static files (outputs directory)
# This must be done after defining routes to avoid conflicts
app.mount("/static", StaticFiles(directory=str(OUTPUTS_DIR / "static")), name="static")
app.mount("/animated", StaticFiles(directory=str(OUTPUTS_DIR / "animated")), name="animated")
app.mount("/assets", StaticFiles(directory=str(OUTPUTS_DIR / "assets")), name="assets")

# Serve metadata and report files directly
@app.get("/metadata.json")
async def get_metadata():
    """Serve metadata JSON file"""
    metadata_path = OUTPUTS_DIR / "metadata.json"
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Metadata not found")
    return FileResponse(metadata_path)


@app.get("/market_report.txt")
async def get_report():
    """Serve market report text file"""
    report_path = OUTPUTS_DIR / "market_report.txt"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report_path, media_type="text/plain")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "path": str(request.url),
            "suggestion": "Check /api/status for available resources"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error("internal_server_error", 
                path=str(request.url), 
                error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "suggestion": "Please check server logs"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )

