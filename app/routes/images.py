from fastapi import APIRouter, HTTPException, Query, Request, Depends, status, Path
from app.utils.helpers import fix_mongo_document, build_query, get_paginated_results, is_authorized
from app.exceptions import UserNotAuthorizedException
from app.models import ImageCreate, ImageUpdate
from app.utils.security import verify_api_key
from app.utils.rate_limiter import rate_limit
from app.utils.cdn import save_image_locally
from app.config import settings
from bson import ObjectId
import os

router = APIRouter()

# Helper Function for Paginated Responses
async def retrieve_images(request: Request, query: dict, page: int, size: int, not_found_msg: str):
    db = request.app.state.db
    collection = db[settings.IMAGES_COLLECTION]
    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(status_code=404, detail=not_found_msg)
    results = await get_paginated_results(collection, query, page, size)
    return results

# SEARCH ENDPOINT
@router.get(
    "/search",
    summary="Search and list images with filters and pagination",
    tags=["Images"]
)
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
    if not (nsfw or category or character or anime or (tags and tags.strip())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one filter must be provided for searching."
        )

    q = build_query(category=category, nsfw=nsfw, character=character, anime=anime, tags=tags)
    results = await get_paginated_results(request.app.state.db[settings.IMAGES_COLLECTION], q, page, size)
    if results["total"] == 0:
        raise HTTPException(status_code=404, detail="No images found with given filters.")
    return results

# ENDPOINT FACTORY FOR SPECIFIC CATEGORIES
def category_endpoint(category_value: str):
    async def endpoint(
        request: Request,
        nsfw: bool = Query(False, description="Filter for NSFW images"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(5, ge=1, description="Number of images per page"),
        user: dict = Depends(verify_api_key),
    ):
        q = build_query(category=category_value, nsfw=nsfw)
        return await retrieve_images(request, q, page, size, f"No {category_value} images found.")
    return endpoint

router.add_api_route("/waifu", category_endpoint("waifu"), methods=["GET"],
                     summary="Retrieve waifu images", tags=["Images"])
router.add_api_route("/husbando", category_endpoint("husbando"), methods=["GET"],
                     summary="Retrieve husbando images", tags=["Images"])
router.add_api_route("/cover", category_endpoint("cover"), methods=["GET"],
                     summary="Retrieve cover images", tags=["Images"])

# RANDOM IMAGE ENDPOINT
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
    q = {}
    if nsfw:
        q["nsfw"] = True
    if character:
        q["character"] = character
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            q["tags"] = {"$in": tag_list}
    return await retrieve_images(request, q, page, size, "No images found with given filters.")

# POST IMAGE ENDPOINT
@router.post("/", summary="Post a new image", tags=["Images"])
@rate_limit
async def post_image(
        request: Request,
        image: ImageCreate,
        user: dict = Depends(verify_api_key)
):
    if not is_authorized(user, "team"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(UserNotAuthorizedException("User is not authorized to post images."))
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

    image_dict["url"] = settings.CDN_DOMAIN.rstrip("/") + "/images" + local_url.replace("/static", "")
    result = await collection.insert_one(image_dict)

    if result.inserted_id:
        image_dict["_id"] = result.inserted_id
        return {"detail": "Image added successfully.", "image": fix_mongo_document(image_dict)}

    raise HTTPException(status_code=500, detail="Error inserting the image into the database.")

# UPDATE IMAGE ENDPOINT
@router.put("/{image_id}", summary="Update an existing image", tags=["Images"])
@rate_limit
async def update_image(
    request: Request,
    image_update: ImageUpdate,
    image_id: str = Path(..., description="The MongoDB ObjectId of the image to update."),
    user: dict = Depends(verify_api_key)
):
    if not is_authorized(user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(UserNotAuthorizedException("User is not authorized to update images."))
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

# DELETE IMAGE ENDPOINT
@router.delete("/{image_id}", summary="Delete an existing image", tags=["Images"])
@rate_limit
async def delete_image(
    request: Request,
    image_id: str = Path(..., description="The MongoDB ObjectId (as a string) of the image to delete."),
    user: dict = Depends(verify_api_key)
):
    if not is_authorized(user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(UserNotAuthorizedException("User is not authorized to delete images."))
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
    local_url = image_doc.get("url")
    if local_url:
        file_path = os.path.join(os.getcwd(), settings.STATIC_IMAGES_DIR, local_url.lstrip("/"))
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting image file: {e}")
    return {"detail": "Image deleted successfully."}