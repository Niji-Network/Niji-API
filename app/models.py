from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional


class APIKeyResponse(BaseModel):
    username: str
    api_key: str
    role: str


class ImageCreate(BaseModel):
    url: HttpUrl = Field(..., description="The source URL of the image to download")
    category: str = Field(..., description="Category of the image (e.g., waifu, husbando, cover, etc.)")
    anime: Optional[str] = Field(None, description="Name of the anime associated with the image")
    nsfw: bool = Field(False, description="Indicates if the image is NSFW")
    character: Optional[List[str]] = Field(None, description="Name of the character featured in the image")
    tags: Optional[List[str]] = Field(None, description="List of tags associated with the image")


class ImageUpdate(BaseModel):
    url: Optional[HttpUrl] = Field(None, description="New source URL of the image")
    category: Optional[str] = Field(None, description="New category of the image")
    anime: Optional[str] = Field(None, description="New anime name associated with the image")
    nsfw: Optional[bool] = Field(None, description="Indicates if the image is NSFW")
    character: Optional[List[str]] = Field(None, description="New character name")
    tags: Optional[List[str]] = Field(None, description="New list of tags")

class GlobalStats(BaseModel):
    totalRequests: int = Field(..., description="Total number of requests received")