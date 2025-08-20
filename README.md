 # File Parser CRUD API

A FastAPI application for uploading and parsing CSV/Excel files with SQLite database storage.

## Features

- Upload CSV and Excel files via REST API
- Automatic file parsing and storage in SQLite database
- List all uploaded files with pagination
- Get file details and parsing progress
- View parsed data with pagination
- Delete files and associated data
- Background processing for file parsing

## Requirements

- Python 3.8+
- All dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd file_parser_crud
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn file_parser_crud.main:app --reload
```

2. The API will be available at:
- Base URL: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative API Documentation: `http://localhost:8000/redoc`

## API Endpoints

### File Operations
- `POST /upload` - Upload a CSV/Excel file
- `GET /files` - List all uploaded files
- `GET /files/{file_id}` - Get file details
- `DELETE /files/{file_id}` - Delete a file and its data

### Data Operations
- `GET /files/{file_id}/rows` - Get parsed rows with pagination
- `GET /files/{file_id}/progress` - Check parsing progress

### Health Check
- `GET /health` - Check API health status

## Usage Examples

### Upload a file using curl:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_file.csv"
```

### List files:
```bash
curl "http://localhost:8000/files"
```

### Get file details:
```bash
curl "http://localhost:8000/files/1"
```

### Get file rows with pagination:
```bash
curl "http://localhost:8000/files/1/rows?skip=0&limit=10"
```

### Check parsing progress:
```bash
curl "http://localhost:8000/files/1/progress"
```

### Delete a file:
```bash
curl -X DELETE "http://localhost:8000/files/1"
```

## File Structure

```
file_parser_crud/
├── file_parser_crud/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── database.py      # Database setup and connection
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   └── parser.py        # File parsing logic
├── uploads/             # Directory for uploaded files
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Database Schema

The application uses SQLite with the following tables:
- `uploaded_files`: Stores metadata about uploaded files
- `file_rows`: Stores parsed data from files

## Error Handling

The API includes comprehensive error handling:
- File type validation
- File size limits (handled by FastAPI)
- Database transaction rollback on errors
- Detailed error messages in responses

## Development

To run tests or make modifications:
1. Ensure the virtual environment is activated
2. Make changes to the code
3. Restart the server if not using `--reload`
4. Check the interactive API documentation at `http://localhost:8000/docs`
