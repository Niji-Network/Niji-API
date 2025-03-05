from fastapi import HTTPException, status
from typing import Any, Dict, Optional
from bson import ObjectId

def fix_mongo_document(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if doc is not None and "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc

def build_query(
    *,
    category: Optional[str] = None,
    nsfw: bool = False,
    character: Optional[str] = None,
    anime: Optional[str] = None,
    tags: Optional[str] = None
) -> Dict[str, Any]:
    query: Dict[str, Any] = {}
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
    return query

async def get_paginated_results(
    collection: Any, query: Dict[str, Any], page: int, size: int
) -> Dict[str, Any]:
    total = await collection.count_documents(query)
    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No images found with given filters."
        )
    skip = (page - 1) * size
    cursor = collection.find(query).skip(skip).limit(size)
    items = await cursor.to_list(length=size)
    return {
        "page": page,
        "size": size,
        "total": total,
        "items": [fix_mongo_document(item) for item in items]
    }

def is_authorized(user: Dict[str, Any], required_role: str) -> bool:
    role_hierarchy = {"user": 1, "team": 2, "admin": 3}
    user_role = user.get("role", "user")
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)