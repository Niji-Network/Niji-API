from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import FileResponse
from app.routes import auth, images, stats
from fastapi import FastAPI, Request
from app.config import settings
import yaml
import os

if not os.path.exists("docs"):
    os.makedirs("docs")

app = FastAPI(
    title="Niji API | Anime related API",
    description=(
        "This API manages anime/manga images. It supports uploading images via a source URL, "
        "saving them locally, and provides endpoints for image management."
    ),
    version="1.0.0",
    redoc_url=None,
    docs_url=None,
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = app.openapi()
    # Write the OpenAPI schema to a YAML file in the "docs" directory.
    openapi_yaml_path = os.path.join("docs", "openapi.yaml")
    with open(openapi_yaml_path, "w") as yaml_file:
        yaml.dump(openapi_schema, yaml_file, sort_keys=False, allow_unicode=True)

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    openapi_yaml_path = os.path.join("docs", "openapi.yaml")
    return FileResponse(openapi_yaml_path, media_type="application/x-yaml")

@app.get("/docs", include_in_schema=False)
async def redoc_docs():
    return get_redoc_html(
        openapi_url="/openapi.yaml",
        title="Niji | Anime related API",
        redoc_favicon_url="/favicon.ico"
    )

# Serve favicon from the STATIC_IMAGES_DIR.
@app.get("/favicon.ico", include_in_schema=False)
async def custom_favicon():
    favicon_path = os.path.join(settings.STATIC_IMAGES_DIR, "favicon.ico")
    return FileResponse(favicon_path)

client = AsyncIOMotorClient(settings.MONGO_URI)
app.state.db = client[settings.DB_NAME]

@app.middleware("http")
async def count_requests(request: Request, call_next):
    db = request.app.state.db
    await db["stats"].update_one(
        {"_id": "global"},
        {"$inc": {"totalRequests": 1}},
        upsert=True
    )
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stats.router, prefix="/v1")
app.include_router(auth.router, prefix="/v1/auth")
app.include_router(images.router, prefix="/v1/img")