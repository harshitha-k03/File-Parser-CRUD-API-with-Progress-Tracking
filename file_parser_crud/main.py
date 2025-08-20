from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import uuid
from typing import List, Optional

from .database import get_db, engine, Base
from . import crud
from .models import UploadedFile
from .schemas import (
    FileUploadResponse, 
    FileListResponse, 
    FileDetailResponse, 
    PaginatedRowsResponse, 
    ProgressResponse, 
    DeleteResponse
)
from .parser import parse_file

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="File Parser CRUD API",
    description="A FastAPI application for uploading and parsing CSV/Excel files",
    version="1.0.0"
)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/")
async def root():
    return {"message": "File Parser CRUD API is running"}

@app.post("/files", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a CSV or Excel file for processing"""
    
    # Validate file type
    allowed_extensions = {'.csv', '.xlsx', '.xls'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        file_size = len(contents)
        
        # Create database entry
        db_file = crud.create_uploaded_file(
            db=db,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension[1:]  # Remove the dot
        )
        
        # Start background processing
        background_tasks.add_task(
            parse_file,
            file_path,
            file_extension[1:],
            db,
            db_file.id
        )
        
        return db_file
        
    except Exception as e:
        # Clean up file if error occurs
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files", response_model=FileListResponse)
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all uploaded files with pagination"""
    files = crud.get_uploaded_files(db, skip=skip, limit=limit)
    total = db.query(crud.UploadedFile).count()
    
    return FileListResponse(files=files, total=total)

@app.get("/files/{file_id}", response_model=FileDetailResponse)
async def get_file_details(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific file"""
    file = crud.get_uploaded_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file

@app.get("/files/{file_id}/rows", response_model=PaginatedRowsResponse)
async def get_file_rows(
    file_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get parsed rows of a file with pagination"""
    file = crud.get_uploaded_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return crud.get_file_rows(db, file_id, skip=skip, limit=limit)

@app.get("/files/{file_id}/progress", response_model=ProgressResponse)
async def get_file_progress(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Check the parsing progress of a file"""
    progress = crud.get_file_progress(db, file_id)
    if not progress:
        raise HTTPException(status_code=404, detail="File not found")
    
    return ProgressResponse(**progress)

@app.delete("/files/{file_id}", response_model=DeleteResponse)
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Delete a file and its associated data"""
    file = crud.get_uploaded_file(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file from disk
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    # Delete from database
    deleted_rows = crud.delete_file_and_rows(db, file_id)
    
    return DeleteResponse(
        message="File deleted successfully",
        deleted_rows=deleted_rows
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
