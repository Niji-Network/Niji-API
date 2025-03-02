from fastapi import HTTPException, Request, status
from app.exceptions import APIKeyException
from app.config import settings


async def verify_api_key(request: Request) -> dict:
    api_key = request.headers.get("X-API-KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(APIKeyException("Missing API key."))
        )

    # Retrieve the database instance stored in app.state.
    db = request.app.state.db
    collection = db[settings.API_KEYS_COLLECTION]

    # Query the collection for the API key.
    key_doc = await collection.find_one({"api_key": api_key})
    if not key_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(APIKeyException("Invalid API key."))
        )

    return key_doc