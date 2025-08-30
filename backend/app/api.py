from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from embeddings import retrieve_answer
from ingest_worker import enqueue_pdf

# Create an API router instance to organize endpoints
router = APIRouter()

# Define the local directory to store uploaded PDF files
PDF_STORAGE_PATH = Path("data/pdfs")

# --- Pydantic Models for Data Validation ---
# These models ensure that the data sent to and from your API is well-structured.

class QueryIn(BaseModel):
    """Input model for a user's query."""
    q: str = Field(..., description="The question to ask the AI model.", min_length=1)

class QueryOut(BaseModel):
    """Output model for the query response."""
    answer: Dict[str, Any]

class UploadOut(BaseModel):
    """Output model for the file upload response."""
    status: str
    filename: str
    path: str

class HealthOut(BaseModel):
    """Output model for the health check."""
    status: str

# --- API Endpoints ---

@router.post(
    "/upload",
    response_model=UploadOut,
    summary="Upload a PDF for processing",
    tags=["Ingestion"]
)
async def upload(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Handles PDF file uploads.

    - **Saves** the uploaded file to a local directory (`data/pdfs`).
    - **Enqueues** a background task to process the PDF for embedding.
    This ensures the user gets a fast response without waiting for the processing to finish.
    """
    try:
        # Ensure the storage directory exists
        PDF_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        
        # Define the full path where the file will be saved
        file_path = PDF_STORAGE_PATH / file.filename
        
        # Asynchronously read the file's contents and write them to disk
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Add the PDF processing task to run in the background
        background_tasks.add_task(enqueue_pdf, str(file_path), {"title": file.filename})

        return {"status": "queued", "filename": file.filename, "path": str(file_path)}
    except Exception as e:
        # If any error occurs during file handling, return a 500 error
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post(
    "/query",
    response_model=QueryOut,
    summary="Query the AI model",
    tags=["Query"]
)
async def query(payload: QueryIn):
    """
    Receives a user's question, retrieves the most relevant information
    from the vector database, and returns it as an answer.
    """
    try:
        # Call the core logic from embeddings.py to get the answer
        answer_data = retrieve_answer(payload.q)
        return {"answer": answer_data}
    except Exception as e:
        # Log the detailed error for debugging purposes on the server
        print(f"Error during query processing: {e}")
        # Return a generic but helpful error message to the user
        raise HTTPException(status_code=500, detail="An error occurred while processing your query.")

@router.get(
    "/health",
    response_model=HealthOut,
    summary="Health check endpoint",
    tags=["Status"]
)
async def health():
    """
    A simple endpoint to verify that the API server is running and responsive.
    Useful for monitoring and uptime checks.
    """
    return {"status": "ok"}

