from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class FileUploadResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    upload_date: datetime
    status: str
    total_rows: int
    processed_rows: int
    
    model_config = ConfigDict(from_attributes=True)

class FileListResponse(BaseModel):
    files: List[FileUploadResponse]
    total: int

class FileDetailResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    upload_date: datetime
    status: str
    total_rows: int
    processed_rows: int
    error_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class FileRowResponse(BaseModel):
    id: int
    row_number: int
    data: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedRowsResponse(BaseModel):
    rows: List[FileRowResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class ProgressResponse(BaseModel):
    file_id: int
    status: str
    total_rows: int
    processed_rows: int
    progress_percentage: float
    error_message: Optional[str] = None

class DeleteResponse(BaseModel):
    message: str
    deleted_rows: int
