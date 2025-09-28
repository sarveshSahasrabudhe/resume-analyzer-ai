from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import tempfile
from resume_analyzer import analyze_resume_with_jd, analyze_resume_only

# Initialize FastAPI app
app = FastAPI(
    title="Resume Analyzer API",
    description="A microservice for analyzing resumes and matching them with job descriptions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class JobDescriptionRequest(BaseModel):
    job_description: str
    required_skills: Optional[List[str]] = None

class ResumeAnalysisResponse(BaseModel):
    resume_skills: List[str]
    jd_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    skills_match_percentage: float
    similarity_score: float
    resume_top_terms: List[dict]
    jd_top_terms: List[dict]
    llm_analysis: str

class ResumeOnlyResponse(BaseModel):
    resume_skills: List[str]
    resume_top_terms: List[dict]
    llm_analysis: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Resume Analyzer API is running"
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Resume Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Analyze resume with job description
@app.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: str = None,
    required_skills: Optional[List[str]] = None
):
    """
    Analyze a resume against a job description
    
    - **resume_file**: PDF file of the resume
    - **job_description**: Text of the job description
    - **required_skills**: Optional list of required skills
    """
    try:
        # Validate file type
        if not resume_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await resume_file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Analyze resume
            result = analyze_resume_with_jd(
                resume_path=tmp_file_path,
                job_description=job_description,
                required_skills=required_skills
            )
            
            return ResumeAnalysisResponse(**result)
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Analyze resume only (without job description)
@app.post("/analyze-resume-only", response_model=ResumeOnlyResponse)
async def analyze_resume_only_endpoint(
    resume_file: UploadFile = File(...)
):
    """
    Analyze a resume without job description comparison
    
    - **resume_file**: PDF file of the resume
    """
    try:
        # Validate file type
        if not resume_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await resume_file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Analyze resume only
            result = analyze_resume_only(resume_path=tmp_file_path)
            
            return ResumeOnlyResponse(**result)
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Get available skills from skills.json
@app.get("/skills")
async def get_available_skills():
    """Get the list of available skills from skills.json"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        skills_path = os.path.join(current_dir, "skills.json")
        
        if not os.path.exists(skills_path):
            raise HTTPException(status_code=404, detail="Skills file not found")
        
        import json
        with open(skills_path, "r") as f:
            skills_data = json.load(f)
        
        return {"skills": skills_data.get("skills", [])}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load skills: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
