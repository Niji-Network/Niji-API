from fastapi import APIRouter, HTTPException, Request, status, Query
from app.models import APIKeyResponse
from app.config import settings
import secrets

router = APIRouter()


@router.post("/create-key", response_model=APIKeyResponse, summary="Create a new API key for a user", tags=["Authentication"])
async def create_api_key(
        request: Request,
        username: str = Query(..., description="Unique username for API key generation")
):
    """
    Creates a new API key for the specified username.

    **Parameters:**
      - **username**: The unique username for which to generate an API key.

    **Raises:**
      - HTTPException (400): If the username already exists.

    **Returns:**
      A JSON document with the username and the generated API key.
    """
    db = request.app.state.db
    collection = db[settings.API_KEYS_COLLECTION]

    # Check if the username already exists in the database.
    existing = await collection.find_one({"username": username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )

    # Generate a secure, random API key.
    api_key = secrets.token_hex(16)
    document = {"username": username, "api_key": api_key}

    # Insert the new API key document into the database.
    await collection.insert_one(document)

    # Return the username and API key as JSON.
    return {"username": username, "api_key": api_key}