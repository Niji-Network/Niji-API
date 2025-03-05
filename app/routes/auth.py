from fastapi import APIRouter, HTTPException, Request, status, Query
from app.models import APIKeyResponse
from app.config import settings
from typing import Dict
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
) -> Dict[str, str]:
    if set(request.query_params.keys()) != {"username"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only the 'username' query parameter is allowed."
        )

    db = request.app.state.db
    collection = db[settings.API_KEYS_COLLECTION]

    if await collection.find_one({"username": username}):
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
