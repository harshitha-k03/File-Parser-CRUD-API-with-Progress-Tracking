from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json

from .models import UploadedFile, FileRow
from .schemas import FileUploadResponse, FileDetailResponse, PaginatedRowsResponse, FileRowResponse

def create_uploaded_file(db: Session, filename: str, original_filename: str, 
                        file_path: str, file_size: int, file_type: str) -> UploadedFile:
    db_file = UploadedFile(
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_uploaded_files(db: Session, skip: int = 0, limit: int = 100) -> List[UploadedFile]:
    return db.query(UploadedFile).offset(skip).limit(limit).all()

def get_uploaded_file(db: Session, file_id: int) -> Optional[UploadedFile]:
    return db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

def update_file_status(db: Session, file_id: int, status: str, 
                      total_rows: int = None, processed_rows: int = None, 
                      error_message: str = None):
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if db_file:
        db_file.status = status
        if total_rows is not None:
            db_file.total_rows = total_rows
        if processed_rows is not None:
            db_file.processed_rows = processed_rows
        if error_message is not None:
            db_file.error_message = error_message
        db.commit()
        db.refresh(db_file)
    return db_file

def create_file_rows(db: Session, file_id: int, rows_data: List[dict]):
    file_rows = []
    for idx, row_data in enumerate(rows_data, 1):
        file_row = FileRow(
            file_id=file_id,
            row_number=idx,
            data=json.dumps(row_data)
        )
        file_rows.append(file_row)
    
    db.add_all(file_rows)
    db.commit()

def get_file_rows(db: Session, file_id: int, skip: int = 0, limit: int = 100) -> PaginatedRowsResponse:
    query = db.query(FileRow).filter(FileRow.file_id == file_id)
    
    total = query.count()
    rows = query.offset(skip).limit(limit).all()
    
    formatted_rows = []
    for row in rows:
        formatted_rows.append(FileRowResponse(
            id=row.id,
            row_number=row.row_number,
            data=json.loads(row.data)
        ))
    
    total_pages = (total + limit - 1) // limit
    
    return PaginatedRowsResponse(
        rows=formatted_rows,
        total=total,
        page=(skip // limit) + 1,
        limit=limit,
        total_pages=total_pages
    )

def delete_file_and_rows(db: Session, file_id: int) -> int:
    # Get the file
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not db_file:
        return 0
    
    # Count rows before deletion
    row_count = db.query(FileRow).filter(FileRow.file_id == file_id).count()
    
    # Delete file and its rows (cascade will handle rows)
    db.delete(db_file)
    db.commit()
    
    return row_count

def get_file_progress(db: Session, file_id: int) -> Optional[dict]:
    db_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not db_file:
        return None
    
    progress_percentage = 0
    if db_file.total_rows > 0:
        progress_percentage = (db_file.processed_rows / db_file.total_rows) * 100
    
    return {
        "file_id": db_file.id,
        "status": db_file.status,
        "total_rows": db_file.total_rows,
        "processed_rows": db_file.processed_rows,
        "progress_percentage": round(progress_percentage, 2),
        "error_message": db_file.error_message
    }
