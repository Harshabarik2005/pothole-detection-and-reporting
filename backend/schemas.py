from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .models import UserRole, ComplaintStatus, ComplaintType

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER

class UserLogin(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ComplaintBase(BaseModel):
    location: str
    road_name: Optional[str] = None
    type: ComplaintType = ComplaintType.MANUAL

class ComplaintCreate(ComplaintBase):
    pass

class PotholeOut(BaseModel):
    id: int
    severity: float
    confidence: float
    frame_timestamp: float

    class Config:
        orm_mode = True

class ComplaintOut(ComplaintBase):
    id: int
    user_id: int
    status: ComplaintStatus
    video_path: Optional[str]
    priority_score: float
    created_at: datetime
    potholes: List[PotholeOut] = []

    class Config:
        orm_mode = True
