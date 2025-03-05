from fastapi import HTTPException
from app.config import settings
from pathlib import Path
import requests
import uuid

def get_extension(image_url: str, content_type: str) -> str:
    content_type = content_type.lower()
    if "image/gif" in content_type:
        return "gif"
    elif "image/png" in content_type:
        return "png"
    elif "image/jpeg" in content_type or "image/jpg" in content_type:
        return "jpg"

    url_lower = image_url.lower()
    if url_lower.endswith((".gif",)):
        return "gif"
    elif url_lower.endswith((".png",)):
        return "png"
    elif url_lower.endswith((".jpeg", ".jpg")):
        return "jpg"
    return "jpg"

def save_image_locally(image_url: str, category: str) -> str:
    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading the image: {e}")

    extension = get_extension(image_url, response.headers.get("Content-Type", ""))
    filename = f"{uuid.uuid4()}.{extension}"

    category_dir = Path(settings.STATIC_IMAGES_DIR) / category
    category_dir.mkdir(parents=True, exist_ok=True)
    file_path = category_dir / filename

    try:
        file_path.write_bytes(response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving the image: {e}")

    return f"/{category}/{filename}"