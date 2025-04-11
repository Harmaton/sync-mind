import structlog
import uvicorn
from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import mindsdb_router, airbyte_router
from settings import Settings

logger = structlog.get_logger(__name__)

settings = Settings()

def create_app() -> FastAPI:
    app = FastAPI(
        title="Sync Mind API",
        description="AI-powered commerce insights for marketplaces",
        version="0.1.0",
        redirect_slashes=False
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    try:
        @app.get("/health")
        async def health_check():
            return {"status": "healthy"}

        # Register routers
        app.include_router(mindsdb_router, prefix="/api")
        app.include_router(airbyte_router, prefix="/api")

    except Exception as e:
        logger.error(f"Error initializing application: {str(e)}")
        raise

    return app

app = create_app()

def start() -> None:
    try:
        logger.info(f"Starting Sync Mind API on port {settings.port}")
        uvicorn.run(app, host=settings.host, port=settings.port)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    start()