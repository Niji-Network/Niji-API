from fastapi import HTTPException
from app.config import settings
import requests
import uuid
import os


def save_image_locally(image_url: str, category: str) -> str:
    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading the image: {e}")

    content_type = response.headers.get("Content-Type", "").lower()
    if "image/gif" in content_type:
        extension = "gif"
    elif "image/png" in content_type:
        extension = "png"
    elif "image/jpeg" in content_type or "image/jpg" in content_type:
        extension = "jpg"
    else:
        url_lower = image_url.lower()
        if url_lower.endswith(".gif"):
            extension = "gif"
        elif url_lower.endswith(".png"):
            extension = "png"
        elif url_lower.endswith(".jpeg"):
            extension = "jpg"
        elif url_lower.endswith(".jpg"):
            extension = "jpg"
        else:
            extension = "jpg"

    image_bytes = response.content
    filename = f"{uuid.uuid4()}.{extension}"

    category_dir = os.path.join(settings.STATIC_IMAGES_DIR, category)
    os.makedirs(category_dir, exist_ok=True)
    file_path = os.path.join(category_dir, filename)

    try:
        with open(file_path, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving the image: {e}")

    return f"/{category}/{filename}"