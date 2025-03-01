from fastapi import APIRouter, HTTPException, Query, Request, Depends, status, Path
from app.utils.helpers import fix_mongo_document  # Helper to convert MongoDB ObjectId to string
from app.models import ImageCreate, ImageUpdate
from app.utils.security import verify_api_key
from app.utils.rate_limiter import rate_limit
from app.utils.cdn import save_image_locally
from app.config import settings
from bson import ObjectId
import random
import os

router = APIRouter()


# -------------------------------
# SEARCH ENDPOINT (with pagination)
# -------------------------------
@router.get("/search", summary="Search and list images with filters and pagination", tags=["Images"])
@rate_limit
async def search_images(
        request: Request,
        nsfw: bool = Query(False, description="Filter for NSFW images"),
        character: str = Query(None, description="Filter by character name"),
        tags: str = Query(None, description="Comma-separated list of tags"),
        anime: str = Query(None, description="Filter by anime name"),
        category: str = Query(None, description="Filter by image category"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(5, ge=1, description="Number of images per page"),
        user: dict = Depends(verify_api_key)
):
    """
    Searches for images based on various filters and returns paginated results.

    **Parameters:**
      - nsfw: Boolean flag to include only NSFW images.
      - character: Filter by the character name.
      - tags: Comma-separated list of tags.
      - anime: Filter by the anime name.
      - category: Filter by the image category.
      - page: The page number (default: 1).
      - size: Number of images per page (default: 5).
      - user: Valid API key required.

    **Returns:**
      A JSON object with keys: page, size, total, and images.
    """
    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]

    # Build the query based on provided filters.
    query = {}
    if nsfw:
        query["nsfw"] = True
    if character:
        query["character"] = character
    if anime:
        query["anime"] = anime
    if category:
        query["category"] = category
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            query["tags"] = {"$in": tag_list}

    # Count total matching documents.
    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(status_code=404, detail="No images found with given filters.")

    # Calculate the number of documents to skip based on the page number.
    skip = (page - 1) * size
    cursor = collection.find(query).skip(skip).limit(size)
    images = await cursor.to_list(length=size)

    return {
        "page": page,
        "size": size,
        "total": total,
        "images": [fix_mongo_document(image) for image in images]
    }


# -------------------------------
# RETRIEVE ENDPOINTS WITH PAGINATION
# (For single category endpoints, we add pagination as well)
# -------------------------------

@router.get("/waifu", summary="Retrieve waifu images", tags=["Images"])
@rate_limit
async def get_waifu(
        request: Request,
        nsfw: bool = Query(False, description="Filter for NSFW images"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(5, ge=1, description="Number of images per page"),
        user: dict = Depends(verify_api_key)
):
    """
    Retrieves waifu images with optional NSFW filtering and pagination.

    **Returns:**
      A paginated JSON object with waifu images.
    """
    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]
    query = {"category": "waifu"}
    if nsfw:
        query["nsfw"] = True

    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(status_code=404, detail="No waifu images found.")

    skip = (page - 1) * size
    cursor = collection.find(query).skip(skip).limit(size)
    images = await cursor.to_list(length=size)

    return {
        "page": page,
        "size": size,
        "total": total,
        "images": [fix_mongo_document(image) for image in images]
    }


@router.get("/husbando", summary="Retrieve husbando images", tags=["Images"])
@rate_limit
async def get_husbando(
        request: Request,
        nsfw: bool = Query(False, description="Filter for NSFW images"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(5, ge=1, description="Number of images per page"),
        user: dict = Depends(verify_api_key)
):
    """
    Retrieves husbando images with optional NSFW filtering and pagination.

    **Returns:**
      A paginated JSON object with husbando images.
    """
    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]
    query = {"category": "husbando"}
    if nsfw:
        query["nsfw"] = True

    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(status_code=404, detail="No husbando images found.")

    skip = (page - 1) * size
    cursor = collection.find(query).skip(skip).limit(size)
    images = await cursor.to_list(length=size)

    return {
        "page": page,
        "size": size,
        "total": total,
        "images": [fix_mongo_document(image) for image in images]
    }


@router.get("/cover", summary="Retrieve cover images", tags=["Images"])
@rate_limit
async def get_cover(
        request: Request,
        nsfw: bool = Query(False, description="Filter for NSFW images"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(5, ge=1, description="Number of images per page"),
        user: dict = Depends(verify_api_key)
):
    """
    Retrieves cover images with optional NSFW filtering and pagination.

    **Returns:**
      A paginated JSON object with cover images.
    """
    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]
    query = {"category": "cover"}
    if nsfw:
        query["nsfw"] = True

    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(status_code=404, detail="No cover images found.")

    skip = (page - 1) * size
    cursor = collection.find(query).skip(skip).limit(size)
    images = await cursor.to_list(length=size)

    return {
        "page": page,
        "size": size,
        "total": total,
        "images": [fix_mongo_document(image) for image in images]
    }


@router.get("/random", summary="Retrieve a random image with optional filters", tags=["Images"])
@rate_limit
async def get_random(
        request: Request,
        nsfw: bool = Query(False, description="Filter for NSFW images"),
        character: str = Query(None, description="Filter by character name"),
        tags: str = Query(None, description="Comma-separated list of tags"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(5, ge=1, description="Number of images per page"),
        user: dict = Depends(verify_api_key)
):
    """
    Retrieves random images with optional filters and pagination.

    **Parameters:**
      - nsfw: Filter for NSFW images.
      - character: Filter by character name.
      - tags: Comma-separated list of tags.
      - page: The page number.
      - size: The number of images per page.

    **Returns:**
      A JSON object with paginated random image results.

    **Raises:**
      HTTPException (404) if no matching images are found.
    """
    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]
    query = {}
    if nsfw:
        query["nsfw"] = True
    if character:
        query["character"] = character
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            query["tags"] = {"$in": tag_list}
    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(status_code=404, detail="No images found with given filters.")

    # For random selection, we can either choose one random image or apply pagination.
    # Here we use pagination to allow random results within a page.
    skip = (page - 1) * size
    cursor = collection.find(query).skip(skip).limit(size)
    images = await cursor.to_list(length=size)
    if images:
        return {
            "page": page,
            "size": size,
            "total": total,
            "images": [fix_mongo_document(image) for image in images]
        }
    raise HTTPException(status_code=404, detail="No images found.")


@router.post("/", summary="Post a new image", tags=["Images"])
@rate_limit
async def post_image(
        request: Request,
        image: ImageCreate,
        user: dict = Depends(verify_api_key)
):
    """
    Saves a new image entry to the database.

    **Requirements:**
      - Downloads the image from the provided URL.
      - Saves the image locally under '/static/images/<category>'.
      - Only users in ALLOWED_POST_USERS are authorized to post images.

    **Parameters:**
      - image: The ImageCreate model containing URL, category, anime, NSFW flag, character, and tags.
      - user: Valid API key required.

    **Returns:**
      A confirmation message along with the saved image document (with ObjectId fixed).

    **Raises:**
      - HTTPException if user is unauthorized, category is missing, or an error occurs.
    """
    if user["username"] not in settings.ALLOWED_POST_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to post images."
        )

    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]
    image_dict = image.dict()
    category = image_dict.get("category")
    if not category:
        raise HTTPException(status_code=400, detail="Category is required.")

    try:
        local_url = save_image_locally(str(image_dict["url"]), category)
    except HTTPException as e:
        raise e

    image_dict["url"] = settings.CDN_DOMAIN.rstrip("/") + local_url.replace("/static", "/images")
    result = await collection.insert_one(image_dict)
    if result.inserted_id:
        image_dict["_id"] = result.inserted_id
        return {"detail": "Image added successfully.", "image": fix_mongo_document(image_dict)}
    raise HTTPException(status_code=500, detail="Error inserting the image into the database.")


@router.put("/{image_id}", summary="Update an existing image", tags=["Images"])
@rate_limit
async def update_image(
        request: Request,
        image_update: ImageUpdate,
        image_id: str = Path(..., description="The MongoDB ObjectId of the image to update."),
        user: dict = Depends(verify_api_key)
):
    """
    Updates an existing image entry in the database.

    Only users in ALLOWED_POST_USERS are authorized to update images.

    **Parameters:**
      - image_id: The MongoDB ObjectId (as a string) of the image to update.
      - image_update: A model with the fields to update (all fields are optional).
      - user: Valid API key required.

    **Returns:**
      A JSON object with a confirmation message and the updated image document (with ObjectId fixed).

    **Raises:**
      - HTTPException (403) if the user is not authorized.
      - HTTPException (400) if the image_id format is invalid.
      - HTTPException (404) if the image is not found.
      - HTTPException (500) if no changes were made.
    """
    if user["username"] not in settings.ALLOWED_POST_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to update images."
        )

    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]
    try:
        obj_id = ObjectId(image_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image_id format.")

    existing_image = await collection.find_one({"_id": obj_id})
    if not existing_image:
        raise HTTPException(status_code=404, detail="Image not found.")

    update_data = image_update.dict(exclude_unset=True)
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
async def delete_image(
        request: Request,
        image_id: str = Path(..., description="The MongoDB ObjectId (as a string) of the image to delete."),
        user: dict = Depends(verify_api_key)
):
    """
    Deletes an image entry from the database and removes the corresponding file from disk.

    Only users in ALLOWED_POST_USERS are authorized to delete images.

    **Parameters:**
      - image_id: The MongoDB ObjectId of the image to delete.
      - user: Valid API key required.

    **Returns:**
      A JSON object with a confirmation message.

    **Raises:**
      - HTTPException (403) if the user is not authorized.
      - HTTPException (400) if the image_id format is invalid.
      - HTTPException (404) if the image is not found.
      - HTTPException (500) if an error occurs during deletion.
    """
    if user["username"] not in settings.ALLOWED_POST_USERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to delete images."
        )

    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]
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

    # Delete the image file from disk.
    local_url = image_doc.get("url")
    if local_url:
        file_path = os.path.join(os.getcwd(), settings.STATIC_IMAGES_DIR, local_url.lstrip("/"))
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting image file: {e}")

    return {"detail": "Image deleted successfully."}
