from app.utils.helpers import fix_mongo_document, build_query, get_paginated_results, is_authorized
from fastapi import APIRouter, HTTPException, Query, Request, Depends, status, Path
from app.exceptions import UserNotAuthorizedException
from app.models import ImageCreate, ImageUpdate
from app.utils.security import verify_api_key
from app.utils.rate_limiter import rate_limit
from app.utils.cdn import save_image_locally
from app.config import settings
from bson import ObjectId
import asyncio
import os

router = APIRouter()

def get_db(request: Request):
    return request.app.state.db

def get_images_collection(db = Depends(get_db)):
    return db[settings.IMAGES_COLLECTION]

async def retrieve_images(
    collection, query: dict, page: int, size: int, not_found_msg: str
) -> dict:
    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(status_code=404, detail=not_found_msg)
    return await get_paginated_results(collection, query, page, size)

@router.get(
    "/search",
    summary="Search and list images with filters and pagination",
    tags=["Images"]
)
@rate_limit
async def search_images(
    nsfw: bool = Query(False, description="Filter for NSFW images"),
    character: str = Query(None, description="Filter by character name"),
    tags: str = Query(None, description="Comma-separated list of tags"),
    anime: str = Query(None, description="Filter by anime name"),
    category: str = Query(None, description="Filter by image category"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(5, ge=1, description="Number of images per page"),
    user: dict = Depends(verify_api_key),
    collection = Depends(get_images_collection)
) -> dict:
    if not (nsfw or category or character or anime or (tags and tags.strip())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one filter must be provided for searching."
        )
    q = build_query(category=category, nsfw=nsfw, character=character, anime=anime, tags=tags)
    return await retrieve_images(collection, q, page, size, "No images found with given filters.")

@router.get(
    "/{category}",
    summary="Retrieve images by category",
    tags=["Images"]
)
@rate_limit
async def get_images_by_category(
    category: str = Path(..., description="Category to filter images"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(5, ge=1, description="Number of images per page"),
    user: dict = Depends(verify_api_key),
    collection = Depends(get_images_collection)
) -> dict:
    query = {"category": category}
    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(status_code=404, detail=f"No images found for category '{category}'.")
    return await get_paginated_results(collection, query, page, size)

@router.get("/random", summary="Retrieve a random image with optional filters", tags=["Images"])
@rate_limit
async def get_random(
    nsfw: bool = Query(False, description="Filter for NSFW images"),
    character: str = Query(None, description="Filter by character name"),
    tags: str = Query(None, description="Comma-separated list of tags"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(5, ge=1, description="Number of images per page"),
    user: dict = Depends(verify_api_key),
    collection = Depends(get_images_collection)
) -> dict:
    q = {}
    if nsfw:
        q["nsfw"] = True
    if character:
        q["character"] = character
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            q["tags"] = {"$in": tag_list}
    return await retrieve_images(collection, q, page, size, "No images found with given filters.")

@router.post("/", summary="Post a new image", tags=["Images"])
@rate_limit
async def post_image(
    image: ImageCreate,
    user: dict = Depends(verify_api_key),
    collection = Depends(get_images_collection)
) -> dict:
    if not is_authorized(user, "team"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(UserNotAuthorizedException("User is not authorized to post images."))
        )
    image_data = image.model_dump()
    category = image_data.get("category")
    if not category:
        raise HTTPException(status_code=400, detail="Category is required.")
    try:
        local_url = save_image_locally(str(image_data["url"]), category)
    except HTTPException as e:
        raise e
    image_data["url"] = settings.CDN_DOMAIN.rstrip("/") + "/images" + local_url.replace("/static", "")
    result = await collection.insert_one(image_data)
    if result.inserted_id:
        image_data["_id"] = result.inserted_id
        return {"detail": "Image added successfully.", "image": fix_mongo_document(image_data)}
    raise HTTPException(status_code=500, detail="Error inserting the image into the database.")

@router.put("/{image_id}", summary="Update an existing image", tags=["Images"])
@rate_limit
async def update_image(
    image_update: ImageUpdate,
    image_id: str = Path(..., description="The MongoDB ObjectId of the image to update."),
    user: dict = Depends(verify_api_key),
    collection = Depends(get_images_collection)
) -> dict:
    if not is_authorized(user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(UserNotAuthorizedException("User is not authorized to update images."))
        )
    try:
        obj_id = ObjectId(image_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image_id format.")
    existing_image = await collection.find_one({"_id": obj_id})
    if not existing_image:
        raise HTTPException(status_code=404, detail="Image not found.")
    update_data = image_update.model_dump(exclude_unset=True)
    if "url" in update_data:
        try:
            new_category = update_data.get("category", existing_image.get("category"))
            local_url = save_image_locally(str(update_data["url"]), new_category)
            update_data["url"] = local_url
        except HTTPException as e:
            raise e
    result = await collection.update_one({"_id": obj_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="No changes made to the image.")
    updated_image = await collection.find_one({"_id": obj_id})
    return {"detail": "Image updated successfully.", "image": fix_mongo_document(updated_image)}

@router.delete("/{image_id}", summary="Delete an existing image", tags=["Images"])
@rate_limit
async def delete_image(
    image_id: str = Path(..., description="The MongoDB ObjectId (as a string) of the image to delete."),
    user: dict = Depends(verify_api_key),
    collection = Depends(get_images_collection)
) -> dict:
    if not is_authorized(user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(UserNotAuthorizedException("User is not authorized to delete images."))
        )
    try:
        obj_id = ObjectId(image_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image_id format.")
    image_doc = await collection.find_one({"_id": obj_id})
    if not image_doc:
        raise HTTPException(status_code=404, detail="Image not found.")
    result = await collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Image not found.")
    local_url = image_doc.get("url")
    if local_url:
        file_path = os.path.join(os.getcwd(), settings.STATIC_IMAGES_DIR, local_url.lstrip("/"))
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting image file: {e}")
    return {"detail": "Image deleted successfully."}