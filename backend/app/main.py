import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router

# Initialize the FastAPI application
app = FastAPI(title="AI Tutor API")

# Define the allowed origins for CORS.
origins = [
    "*", # Using wildcard for simple local development
]

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CRITICAL: This prefix is combined with the path in api.py
# It MUST be exactly "/api/v1"
app.include_router(api_router, prefix="/api/v1")

@app.get("/", summary="Root endpoint to check server status")
async def root():
    return {"status": "ok", "message": "AI Tutor Backend is running"}

# This block allows you to run the server directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

