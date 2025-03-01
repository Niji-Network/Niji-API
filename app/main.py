from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import FileResponse
from app.routes import auth, images, stats
from app.config import settings
import os

# Initialize FastAPI application with custom configuration.
app = FastAPI(
    title="Niji API | Anime related API",
    description=(
        "This API manages anime/manga images. It supports uploading images via a source URL, "
        "saving them locally, and provides endpoints for image management."
    ),
    version="1.0.0",
    redoc_url=None,  # Disable default ReDoc endpoint (we use a custom one)
    docs_url=None,   # Disable default Swagger UI endpoint
)

# Custom ReDoc endpoint with a custom favicon.
@app.get("/docs", include_in_schema=False)
async def redoc_docs():
    """
    Returns the custom ReDoc HTML documentation with a custom favicon.
    """
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Niji | Anime related API",
        redoc_favicon_url="/favicon.ico"  # Uses an absolute URL for the favicon.
    )

# Endpoint to serve the favicon.
@app.get("/favicon.ico", include_in_schema=False)
async def custom_favicon():
    """
    Serves the favicon from the static folder.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to the favicon file.
    favicon_path = os.path.join(base_dir, "..", "static", "favicon.ico")
    return FileResponse(favicon_path)

# Initialize MongoDB client using connection string from settings.
client = AsyncIOMotorClient(settings.MONGO_URI)
# Store the database instance in app.state for global access.
app.state.db = client[settings.DB_NAME]

# Add CORS middleware to allow cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for modular endpoints.
# - Status endpoint (e.g., for resource consumption).
app.include_router(stats.router, prefix="/v1")
# - Authentication endpoints.
app.include_router(auth.router, prefix="/v1/auth")
# - Image endpoints; using versioned API prefix (e.g., /v1).
app.include_router(images.router, prefix="/v1/img")

# Note:
# This setup provides a custom /docs endpoint (using ReDoc with your favicon),
# initializes MongoDB using environment settings, adds global CORS settings,
# and includes modular routers for authentication, image management, and status.