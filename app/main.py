from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from app.routes import auth, images, stats
from pymongo.errors import PyMongoError
from app.config import settings
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = AsyncIOMotorClient(settings.MONGO_URI) # type: ignore
    app.state.db = app.state.client[settings.DB_NAME] # type: ignore

    favicon_path = os.path.join(settings.STATIC_IMAGES_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        with open(favicon_path, "rb") as f:
            app.state.favicon_data = f.read() # type: ignore
    else:
        app.state.favicon_data = None # type: ignore

    yield

    app.state.client.close()

app = FastAPI(
    title="Niji API | Anime related API",
    redoc_url=None,
    docs_url=None,
    lifespan=lifespan,
)

@app.middleware("http")
async def count_requests(request: Request, call_next):
    try:
        await request.app.state.db["stats"].update_one(
            {"_id": "global"},
            {"$inc": {"totalRequests": 1}},
            upsert=True
        )
    except PyMongoError as e:
        pass
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stats.router, prefix="/v1")
app.include_router(auth.router, prefix="/v1/auth")
app.include_router(images.router, prefix="/v1/img")

@app.get("/favicon.ico", include_in_schema=False)
async def custom_favicon():
    if app.state.favicon_data: # type: ignore
        return Response(content=app.state.favicon_data, media_type="image/x-icon") # type: ignore
    raise HTTPException(status_code=404, detail="Favicon not found")