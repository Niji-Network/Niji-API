from fastapi import HTTPException
from app.config import settings
import requests
import uuid
import os


def save_image_locally(image_url: str, category: str) -> str:
    """
    Downloads an image from the provided URL and saves it locally in a folder based on the given category.

    The image is saved under: <STATIC_IMAGES_DIR>/<category>/<filename> where the filename is generated uniquely
    and its extension is determined by the image's MIME type. Supported formats: GIF, PNG, JPG, JPEG.

    Parameters:
        image_url (str): The URL of the image to download.
        category (str): The category under which the image should be stored.

    Returns:
        str: The relative URL (e.g., "/<category>/<filename>") that NGINX will serve.

    Raises:
        HTTPException: If there is an error downloading the image (HTTP 400) or saving the image (HTTP 500).
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading the image: {e}")

    # Determine the file extension based on the Content-Type header.
    content_type = response.headers.get("Content-Type", "").lower()
    if "image/gif" in content_type:
        extension = "gif"
    elif "image/png" in content_type:
        extension = "png"
    elif "image/jpeg" in content_type or "image/jpg" in content_type:
        extension = "jpg"
    else:
        # Fallback to checking the URL extension if available.
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
    # Generate a unique filename with the determined extension.
    filename = f"{uuid.uuid4()}.{extension}"

    # Build the directory path to save the image.
    category_dir = os.path.join(settings.STATIC_IMAGES_DIR, category)
    os.makedirs(category_dir, exist_ok=True)
    file_path = os.path.join(category_dir, filename)

    try:
        with open(file_path, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving the image: {e}")

    # Return the relative URL that NGINX will serve.
    return f"/{category}/{filename}"