from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.routes import auth, images, stats
from fastapi import FastAPI, Request
from app.config import settings
import os

app = FastAPI(
    title="Niji API | Anime related API",
    redoc_url=None,
    docs_url=None,
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