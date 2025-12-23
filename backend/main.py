from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import shutil
import os
import uuid
from . import models, schemas, crud, database, auth, yolo_service

app = FastAPI(title="Pothole Detection API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Auth Routes
@app.post("/auth/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)

@app.post("/auth/token", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.UserLogin, db: AsyncSession = Depends(database.get_db)):
    user = await crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "username": user.username}

# Complaint Routes
@app.post("/complaints/", response_model=schemas.ComplaintOut)
async def create_complaint(
    location: str = Form(...),
    road_name: Optional[str] = Form(None),
    type: str = Form("manual"),
    video: UploadFile = File(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    video_path = None
    if video:
        # Save video
        file_ext = video.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        video_path = os.path.join(upload_dir, file_name)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

    complaint_data = schemas.ComplaintCreate(location=location, road_name=road_name, type=type)
    complaint = await crud.create_complaint(db, complaint_data, current_user.id, video_path)

    # Trigger processing if video exists (simple sync trigger for MVP)
    if video_path and type == "automated":
        # Process and update priority
        # In prod, this should be a background task
        # For demo, we might await it or fire and forget
        # We'll use our async service wrapper
        potholes = await yolo_service.analyze_video(video_path)
        await crud.add_potholes(db, complaint.id, potholes)
        
        # Calculate priority (Simple Algorithm)
        # Priority = sum(severity * confidence)
        total_score = sum([p['severity'] * p['confidence'] for p in potholes])
        await crud.update_complaint_priority(db, complaint.id, total_score)
        
        # Refetch to get updated data
        result = await db.execute(models.select(models.Complaint).where(models.Complaint.id == complaint.id).options(models.selectinload(models.Complaint.potholes)))
        complaint = result.scalars().first()

    return complaint

@app.get("/complaints/my", response_model=List[schemas.ComplaintOut])
async def read_my_complaints(current_user: models.User = Depends(auth.get_current_user), db: AsyncSession = Depends(database.get_db)):
    return await crud.get_complaints(db, user_id=current_user.id)

@app.get("/complaints/all", response_model=List[schemas.ComplaintOut])
async def read_all_complaints(current_user: models.User = Depends(auth.get_current_user), db: AsyncSession = Depends(database.get_db)):
    if current_user.role != models.UserRole.EMPLOYEE:
         raise HTTPException(status_code=403, detail="Not authorized")
    return await crud.get_complaints(db)

@app.put("/complaints/{complaint_id}/status", response_model=schemas.ComplaintOut)
async def update_status(
    complaint_id: int, 
    status: models.ComplaintStatus,
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    if current_user.role != models.UserRole.EMPLOYEE:
         raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(models.select(models.Complaint).where(models.Complaint.id == complaint_id))
    complaint = result.scalars().first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = status
    await db.commit()
    await db.refresh(complaint)
    return complaint

# Mount static files for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
