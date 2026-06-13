from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import json
from backend.utils import extract_text_from_pdf, validate_pdf_file, extract_candidate_name_from_pdf, get_skills_from_description
from backend.analyzer import get_analyzer
from backend.database import save_analysis
from backend.models import AnalyzeResponse, CandidateResult, AnalysisStatistics
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Analysis"])

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resumes(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...),
    sensitivity: float = Form(0.5),
    skill_weights: str = Form("{}"),        # JSON string: {"Python": 3.0, "React": 2.0}
    strict_mode: bool = Form(False),         # True = exact match only
    groq_api_key: str = Form("")            # Optional user-provided API key
):
    """
    Analyze uploaded resumes against job description
    
    Args:
        files: PDF resume files
        job_description: Job description text
        sensitivity: Matching threshold (0.3-0.9)
    
    Returns:
        Analysis results with candidates and statistics
    """
    
    # Validation
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 resumes allowed per analysis")
    
    if not job_description or len(job_description) < 10:
        raise HTTPException(status_code=400, detail="Job description too short")
    
    if sensitivity < 0.3 or sensitivity > 0.9:
        raise HTTPException(status_code=400, detail="Sensitivity must be between 0.3 and 0.9")
    
    # Parse skill weights JSON
    try:
        parsed_weights = json.loads(skill_weights) if skill_weights else {}
        # Clamp weights to 1.0–5.0
        parsed_weights = {k: max(1.0, min(5.0, float(v))) for k, v in parsed_weights.items()}
    except (json.JSONDecodeError, ValueError):
        parsed_weights = {}
    
    # Validate file types
    for file in files:
        if not validate_pdf_file(file.filename):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
    
    try:
        # Extract required skills from job description
        required_skills = get_skills_from_description(job_description, max_skills=15)
        
        if not required_skills:
            raise HTTPException(status_code=400, detail="Could not extract skills from job description")
        
        # Initialize analyzer
        analyzer = get_analyzer(sensitivity=sensitivity)
        
        # Process each resume
        candidates_data = []
        for file in files:
            # Read PDF
            content = await file.read()
            resume_text, extract_error = extract_text_from_pdf(content)
            
            if extract_error or not resume_text:
                logger.warning(f"Skipping {file.filename}: {extract_error}")
                processing_errors.append({"file": file.filename, "error": extract_error or "No text extracted"})
                continue
            
            # Extract candidate name
            candidate_name = extract_candidate_name_from_pdf(resume_text)
            
            # Analyze resume
            analysis = analyzer.analyze_resume(resume_text, required_skills, parsed_weights, strict_mode)
            analysis['name'] = candidate_name or file.filename.replace('.pdf', '')
            
            candidates_data.append(analysis)
        
        if not candidates_data:
            raise HTTPException(status_code=400, detail="Could not extract text from any PDF")
        
        # Calculate statistics
        matched_counts = [c['matched_count'] for c in candidates_data]
        avg_score = sum(matched_counts) / len(matched_counts) if matched_counts else 0
        
        # Find most matched skill
        all_matched = []
        for candidate in candidates_data:
            all_matched.extend(candidate['matched_skills'])
        
        skill_counts = {}
        for skill in all_matched:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        most_matched_skill = max(skill_counts, key=skill_counts.get) if skill_counts else None
        
        # Find least matched skill
        all_missing = []
        for candidate in candidates_data:
            all_missing.extend(candidate['missing_skills'])
        
        missing_counts = {}
        for skill in all_missing:
            missing_counts[skill] = missing_counts.get(skill, 0) + 1
        
        least_matched = max(missing_counts, key=missing_counts.get) if missing_counts else None
        
        # Build response
        candidates_response = [
            CandidateResult(
                name=c['name'],
                matched_count=c['matched_count'],
                missing_count=c['missing_count'],
                match_percentage=c['match_percentage'],
                weighted_score=c.get('weighted_score'),
                total_weighted=c.get('total_weighted'),
                max_weighted=c.get('max_weighted'),
                matched_skills=c['matched_skills'],
                missing_skills=c['missing_skills'],
                suggestions=c.get('suggestions', [])
            )
            for c in candidates_data
        ]
        
        statistics = AnalysisStatistics(
            average_score=avg_score / 15,  # Normalize to 0-1
            most_matched_skill=most_matched_skill,
            least_matched_skill=least_matched,
            total_unique_skills=len(required_skills)
        )
        
        # Save to database
        results = {
            'candidates': [c.dict() for c in candidates_response],
            'statistics': statistics.dict()
        }
        analysis_id = save_analysis(job_description, results)
        
        return AnalyzeResponse(
            analysis_id=analysis_id,
            candidates=candidates_response,
            statistics=statistics,
            timestamp=datetime.now()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")