import structlog
import uvicorn
from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import mindsdb_router, airbyte_router
from router.slack import slack_router
from settings import Settings
from mindsdb import mindsdb_setup
from airbyte import setup_airbyte_connections

logger = structlog.get_logger(__name__)

settings = Settings()

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    This function:
      1. Creates a new FastAPI instance with optional CORS middleware.
      2. Loads configuration.
      3. Sets up the airbyte pipeline
      4. Sets up the MindsDB instance
      5. Sets up the Slack chatbot and knowledge base
      6. Registers routers for airbyte, mindsdb, and slack
        
    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    app = FastAPI(
        title="Sync Mind API",
        description="AI-powered commerce insights for marketplaces",
        version="0.1.0",
        redirect_slashes=False
    )

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    try:
        # Run Airbyte Pipeline Sync
        setup_airbyte_connections()

        # Setup Slack chatbot and knowledge base
        mindsdb_setup()

        # # Setup Text2SQL skill
        # setup_text2sql_skill()
        
        # # Setup Forecasting model
        # setup_forecast_model()
        

        # Register routers
        app.include_router(mindsdb_router, prefix="/api")
        app.include_router(airbyte_router, prefix="/api")
        app.include_router(slack_router, prefix="/api")

    except Exception as e:
        logger.error(f"Error initializing application: {str(e)}")
        raise

    return app

app = create_app()

def start() -> None:
    try:
        logger.info(f"Starting Sync Mind API on port {settings.port}")
        uvicorn.run(app, host="0.0.0.0", port=8080)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    start()