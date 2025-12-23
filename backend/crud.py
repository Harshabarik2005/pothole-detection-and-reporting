from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from . import models, schemas, auth

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, password_hash=hashed_password, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_complaint(db: AsyncSession, complaint: schemas.ComplaintCreate, user_id: int, video_path: str = None):
    db_complaint = models.Complaint(
        user_id=user_id,
        location=complaint.location,
        road_name=complaint.road_name,
        type=complaint.type,
        video_path=video_path,
        status=models.ComplaintStatus.PENDING
    )
    db.add(db_complaint)
    await db.commit()
    await db.refresh(db_complaint)
    return db_complaint

async def get_complaints(db: AsyncSession, user_id: int = None, skip: int = 0, limit: int = 100):
    query = select(models.Complaint).options(selectinload(models.Complaint.potholes)).offset(skip).limit(limit)
    if user_id:
        query = query.where(models.Complaint.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()

async def add_potholes(db: AsyncSession, complaint_id: int, potholes: list):
    for p in potholes:
        db_pothole = models.Pothole(
            complaint_id=complaint_id,
            severity=p['severity'],
            confidence=p['confidence'],
            frame_timestamp=p['frame_timestamp']
        )
        db.add(db_pothole)
    await db.commit()

async def update_complaint_priority(db: AsyncSession, complaint_id: int, score: float):
    # This might need to be optimized to not run a full fetch
    result = await db.execute(select(models.Complaint).where(models.Complaint.id == complaint_id))
    complaint = result.scalars().first()
    if complaint:
        complaint.priority_score = score
        await db.commit()
