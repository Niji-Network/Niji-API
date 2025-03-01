from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional


class APIKeyResponse(BaseModel):
    """
    Response model for API key creation.

    Attributes:
      - username: The username associated with the API key.
      - api_key: The generated API key.
    """
    username: str
    api_key: str


class ImageCreate(BaseModel):
    """
    Request model for creating a new image entry.

    Attributes:
      - url: The source URL of the image to download.
      - category: The category of the image (e.g., waifu, husbando, cover, etc.).
      - anime: (Optional) The name of the anime associated with the image.
      - nsfw: A flag indicating if the image is NSFW. Defaults to False.
      - character: (Optional) The name of the character featured in the image.
      - tags: (Optional) A list of tags associated with the image.
    """
    url: HttpUrl = Field(..., description="The source URL of the image to download")
    category: str = Field(..., description="Category of the image (e.g., waifu, husbando, cover, etc.)")
    anime: Optional[str] = Field(None, description="Name of the anime associated with the image")
    nsfw: bool = Field(False, description="Indicates if the image is NSFW")
    character: Optional[str] = Field(None, description="Name of the character featured in the image")
    tags: Optional[List[str]] = Field(None, description="List of tags associated with the image")


class ImageUpdate(BaseModel):
    """
    Request model for updating an existing image entry.

    All fields are optional; only the provided fields will be updated.

    Attributes:
      - url: (Optional) New source URL for the image.
      - category: (Optional) New category for the image.
      - anime: (Optional) New anime name associated with the image.
      - nsfw: (Optional) New NSFW flag.
      - character: (Optional) New character name.
      - tags: (Optional) New list of tags.
    """
    url: Optional[HttpUrl] = Field(None, description="New source URL of the image")
    category: Optional[str] = Field(None, description="New category of the image")
    anime: Optional[str] = Field(None, description="New anime name associated with the image")
    nsfw: Optional[bool] = Field(None, description="Indicates if the image is NSFW")
    character: Optional[str] = Field(None, description="New character name")
    tags: Optional[List[str]] = Field(None, description="New list of tags")
