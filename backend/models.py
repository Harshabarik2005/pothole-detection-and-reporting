from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .database import Base
import datetime
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    EMPLOYEE = "employee"

class ComplaintStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FIXED = "fixed"

class ComplaintType(str, enum.Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default=UserRole.USER)

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, default=ComplaintType.MANUAL)
    status = Column(String, default=ComplaintStatus.PENDING)
    location = Column(String) # "lat,long"
    road_name = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    priority_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="complaints")
    potholes = relationship("Pothole", backref="complaint")

class Pothole(Base):
    __tablename__ = "potholes"
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    severity = Column(Float)
    confidence = Column(Float)
    frame_timestamp = Column(Float)
