import os
import tempfile
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from backend.services.milvus_service import MilvusService
from backend.services.groq_service import GroqService
from backend.services.cv_processor import CVProcessor
from backend.services.job_embedder import JobEmbedder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HRSD Job Matching API",
    description="AI-powered job matching system for Human Resources and Social Development ministry",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
milvus_service = None
groq_service = None
cv_processor = None
job_embedder = None

# Pydantic models
class JobMatchRequest(BaseModel):
    cv_text: str
    top_k: int = 10

class JobMatchResponse(BaseModel):
    matches: List[Dict[str, Any]]
    analysis: str
    cv_summary: Dict[str, Any]

class JobUploadResponse(BaseModel):
    message: str
    inserted_count: int

class CollectionStatsResponse(BaseModel):
    collection_name: str
    row_count: int
    prefix: str
    base_name: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global milvus_service, groq_service, cv_processor, job_embedder
    
    try:
        logger.info("Initializing HRSD Job Matching services...")
        
        # Initialize services
        milvus_service = MilvusService()
        groq_service = GroqService()
        cv_processor = CVProcessor()
        job_embedder = JobEmbedder()
        
        # Initialize Milvus
        await milvus_service.initialize()
        await job_embedder.initialize()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "HRSD Job Matching API"}

# CV processing endpoints
@app.post("/upload-cv", response_model=Dict[str, Any])
async def upload_cv(file: UploadFile = File(...)):
    """Upload and process a CV file"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process CV
            cv_data = await cv_processor.process_cv(tmp_file_path, file.filename)
            
            return {
                "message": "CV processed successfully",
                "cv_data": cv_data,
                "filename": file.filename
            }
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Error processing CV: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing CV: {str(e)}")

@app.post("/match-jobs", response_model=JobMatchResponse)
async def match_jobs(request: JobMatchRequest):
    """Match jobs based on CV text"""
    try:
        # Search for matching jobs
        matched_jobs = await milvus_service.search_jobs(request.cv_text, request.top_k)
        
        # Process CV data for analysis
        cv_data = await cv_processor.process_cv_from_text(request.cv_text)
        
        # Generate AI analysis
        analysis = await groq_service.generate_job_matching_response(
            cv_data, matched_jobs
        )
        
        return JobMatchResponse(
            matches=matched_jobs,
            analysis=analysis,
            cv_summary=cv_data
        )
        
    except Exception as e:
        logger.error(f"Error matching jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error matching jobs: {str(e)}")

@app.post("/upload-cv-and-match", response_model=JobMatchResponse)
async def upload_cv_and_match(
    file: UploadFile = File(...),
    top_k: int = 10
):
    """Upload CV and get job matches in one request"""
    try:
        # Process CV
        cv_response = await upload_cv(file)
        cv_data = cv_response["cv_data"]
        
        # Get job matches
        request = JobMatchRequest(cv_text=cv_data["raw_text"], top_k=top_k)
        match_response = await match_jobs(request)
        
        return match_response
        
    except Exception as e:
        logger.error(f"Error in upload and match: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Job management endpoints
@app.post("/add-jobs", response_model=JobUploadResponse)
async def add_jobs(file: UploadFile = File(...)):
    """Add jobs from CSV or JSON file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Determine file type and process
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext == '.csv':
                result = await job_embedder.add_jobs_from_csv(tmp_file_path)
            elif file_ext == '.json':
                result = await job_embedder.add_jobs_from_json(tmp_file_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or JSON.")
            
            return JobUploadResponse(
                message=result.get("message", "Jobs added successfully"),
                inserted_count=result.get("inserted_count", 0)
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        logger.error(f"Error adding jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding jobs: {str(e)}")

@app.post("/add-sample-jobs", response_model=JobUploadResponse)
async def add_sample_jobs():
    """Add sample job data for testing"""
    try:
        sample_jobs = job_embedder.create_sample_jobs()
        result = await job_embedder.add_single_job(sample_jobs[0])  # Add first sample job
        
        # Add remaining jobs
        for job in sample_jobs[1:]:
            await job_embedder.add_single_job(job)
        
        return JobUploadResponse(
            message="Sample jobs added successfully",
            inserted_count=len(sample_jobs)
        )
        
    except Exception as e:
        logger.error(f"Error adding sample jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding sample jobs: {str(e)}")

@app.get("/collection-stats", response_model=CollectionStatsResponse)
async def get_collection_stats():
    """Get collection statistics"""
    try:
        stats = await job_embedder.get_collection_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return CollectionStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

# Chat endpoint for interactive job matching
class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, str]]] = []

@app.post("/chat")
async def chat_with_advisor(request: ChatRequest):
    """Chat with the AI career advisor"""
    try:
        # For now, return a simple response
        # This can be enhanced to provide more interactive job matching
        response = await groq_service.generate_simple_chat_response(
            query=request.message,
            chat_history=request.chat_history
        )
        
        return {
            "response": response,
            "timestamp": "2024-01-01T00:00:00Z"  # Add proper timestamp
        }
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HRSD Job Matching API",
        "version": "1.0.0",
        "description": "AI-powered job matching system for Human Resources and Social Development ministry",
        "endpoints": {
            "health": "/health",
            "upload_cv": "/upload-cv",
            "match_jobs": "/match-jobs",
            "upload_cv_and_match": "/upload-cv-and-match",
            "add_jobs": "/add-jobs",
            "add_sample_jobs": "/add-sample-jobs",
            "collection_stats": "/collection-stats",
            "chat": "/chat"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app_hrsd:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
