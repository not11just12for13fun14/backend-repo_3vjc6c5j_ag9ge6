"""
Database Schemas for the Curtains website

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Product(BaseModel):
    """
    Products collection schema
    Collection: "product"
    """
    slug: str = Field(..., description="URL-friendly unique id")
    title: Dict[str, str] = Field(..., description="Localized titles: {'en': str, 'ar': str}")
    description: Dict[str, str] = Field(default_factory=dict, description="Localized descriptions")
    category: str = Field(..., description="One of the predefined categories")
    image: str = Field(..., description="Main image URL")
    gallery: List[str] = Field(default_factory=list, description="Gallery image URLs")


class GalleryItem(BaseModel):
    """
    Gallery items shown in the gallery page
    Collection: "galleryitem"
    """
    category: str = Field(..., description="Gallery filter category (e.g., living, bedrooms, majlis, offices, custom)")
    image: str = Field(..., description="Image URL")
    title: Dict[str, str] = Field(default_factory=dict, description="Localized optional title")


class ContactMessage(BaseModel):
    """
    Contact form submissions
    Collection: "contactmessage"
    """
    name: str
    phone: str
    message: str
    source: Optional[str] = Field(None, description="Where the message came from (page)")
