"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Core content types for a modern news/political website

class Post(BaseModel):
    """
    News posts and articles
    Collection name: "post"
    """
    title: str = Field(..., description="Post title")
    summary: str = Field(..., description="Short summary/lede")
    content: str = Field(..., description="HTML or Markdown content body")
    cover_image: Optional[str] = Field(None, description="Hero/cover image URL")
    tags: List[str] = Field(default_factory=list, description="Topic tags")
    author: Optional[str] = Field(None, description="Author or source")
    published_at: Optional[datetime] = Field(None, description="Publication datetime")
    featured: bool = Field(False, description="Mark as featured for homepage hero")

class Event(BaseModel):
    """
    Events, rallies, meetings
    Collection name: "event"
    """
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event details")
    location: str = Field(..., description="City/Venue")
    date: datetime = Field(..., description="Event date/time")
    image: Optional[str] = Field(None, description="Event image URL")
    link: Optional[str] = Field(None, description="External or internal link")

class Media(BaseModel):
    """
    Media gallery items (photos/videos)
    Collection name: "media"
    """
    title: str = Field(..., description="Media title")
    type: str = Field(..., description="photo | video")
    url: str = Field(..., description="Media URL")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")

# Example legacy schemas kept for reference (not used by the app directly)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
