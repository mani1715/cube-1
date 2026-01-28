from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Any
import uuid


class AdminLogin(BaseModel):
    """Schema for admin login request"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class AdminToken(BaseModel):
    """Schema for admin token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 480  # minutes


class Admin(BaseModel):
    """Admin user model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    role: str = "admin"  # super_admin, admin, or viewer
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    last_login: datetime = Field(default_factory=datetime.utcnow)


class AdminCreate(BaseModel):
    """Schema for creating an admin"""
    email: EmailStr
    password: str = Field(..., min_length=8)


# Admin Activity Log Model
class AdminActivityLog(BaseModel):
    """Schema for admin activity logging"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    admin_email: str
    action: str  # create, update, delete, status_change, login, logout
    entity: str  # sessions, events, blogs, etc.
    entity_id: str = ""
    details: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Refresh Token Model
class RefreshToken(BaseModel):
    """Schema for refresh token storage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_revoked: bool = False


# Pagination Response Model
class PaginatedResponse(BaseModel):
    """Schema for paginated API responses"""
    data: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int

