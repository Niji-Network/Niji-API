from fastapi import APIRouter, HTTPException, Request, status, Query
from app.models import APIKeyResponse
from app.config import settings
import secrets

router = APIRouter()


@router.post(
    "/create-key",
    response_model=APIKeyResponse,
    summary="Create a new API key for a user",
    tags=["Authentication"]
)
async def create_api_key(
    request: Request,
    username: str = Query(
        ...,
        description="Unique username for API key generation (max 16 characters)",
        max_length=16
    )
):
    if len(request.query_params) != 1 or "username" not in request.query_params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only the 'username' query parameter is allowed."
        )

    db = request.app.state.db
    collection = db[settings.API_KEYS_COLLECTION]

    existing = await collection.find_one({"username": username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )

    api_key = secrets.token_hex(16)
    document = {"username": username, "api_key": api_key, "role": "user"}

    await collection.insert_one(document)
    await db["stats"].update_one(
        {"_id": "global"},
        {"$inc": {"totalUsers": 1}},
        upsert=True
    )

    return {"username": username, "api_key": api_key, "role": "user"}