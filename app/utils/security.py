from fastapi import HTTPException, Request, status
from app.exceptions import APIKeyException
from app.config import settings
from typing import Any, Dict

API_KEY_HEADER = "X-API-KEY"


async def verify_api_key(request: Request) -> Dict[str, Any]:
    api_key = request.headers.get(API_KEY_HEADER)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(APIKeyException("Missing API key."))
        )

    db = request.app.state.db
    collection = db[settings.API_KEYS_COLLECTION]

    key_doc = await collection.find_one({"api_key": api_key})
    if not key_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(APIKeyException("Invalid API key."))
        )

    return key_doc