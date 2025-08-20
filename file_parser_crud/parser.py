import pandas as pd
import os
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import logging

from . import crud

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_csv_file(file_path: str, db: Session, file_id: int) -> Dict[str, Any]:
    """Parse CSV file and store data in database"""
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Convert DataFrame to list of dictionaries
        rows_data = df.to_dict('records')
        
        # Update file status
        crud.update_file_status(
            db, file_id, "processing", 
            total_rows=len(rows_data), 
            processed_rows=0
        )
        
        # Process in batches to update progress
        batch_size = 100
        for i in range(0, len(rows_data), batch_size):
            batch = rows_data[i:i+batch_size]
            crud.create_file_rows(db, file_id, batch)
            
            # Update progress
            processed = min(i + batch_size, len(rows_data))
            crud.update_file_status(
                db, file_id, "processing", 
                processed_rows=processed
            )
        
        # Mark as completed
        crud.update_file_status(
            db, file_id, "completed", 
            processed_rows=len(rows_data)
        )
        
        return {
            "success": True,
            "total_rows": len(rows_data),
            "message": "File parsed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error parsing CSV file: {str(e)}")
        crud.update_file_status(
            db, file_id, "failed", 
            error_message=str(e)
        )
        return {
            "success": False,
            "error": str(e)
        }

def parse_excel_file(file_path: str, db: Session, file_id: int) -> Dict[str, Any]:
    """Parse Excel file and store data in database"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Convert DataFrame to list of dictionaries
        rows_data = df.to_dict('records')
        
        # Update file status
        crud.update_file_status(
            db, file_id, "processing", 
            total_rows=len(rows_data), 
            processed_rows=0
        )
        
        # Process in batches to update progress
        batch_size = 100
        for i in range(0, len(rows_data), batch_size):
            batch = rows_data[i:i+batch_size]
            crud.create_file_rows(db, file_id, batch)
            
            # Update progress
            processed = min(i + batch_size, len(rows_data))
            crud.update_file_status(
                db, file_id, "processing", 
                processed_rows=processed
            )
        
        # Mark as completed
        crud.update_file_status(
            db, file_id, "completed", 
            processed_rows=len(rows_data)
        )
        
        return {
            "success": True,
            "total_rows": len(rows_data),
            "message": "File parsed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error parsing Excel file: {str(e)}")
        crud.update_file_status(
            db, file_id, "failed", 
            error_message=str(e)
        )
        return {
            "success": False,
            "error": str(e)
        }

def parse_file(file_path: str, file_type: str, db: Session, file_id: int) -> Dict[str, Any]:
    """Main function to parse file based on type"""
    if file_type.lower() == 'csv':
        return parse_csv_file(file_path, db, file_id)
    elif file_type.lower() in ['xlsx', 'xls']:
        return parse_excel_file(file_path, db, file_id)
    else:
        crud.update_file_status(
            db, file_id, "failed", 
            error_message=f"Unsupported file type: {file_type}"
        )
        return {
            "success": False,
            "error": f"Unsupported file type: {file_type}"
        }
