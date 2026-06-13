from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ================================================
# REQUEST MODELS
# ================================================

class AnalyzeRequest(BaseModel):
    """Request model for resume analysis"""
    job_description: str = Field(..., min_length=10, description="Job description text")
    sensitivity: float = Field(0.5, ge=0.3, le=0.9, description="Matching sensitivity (0.3-0.9)")

class CompareRequest(BaseModel):
    """Request model for comparing candidates"""
    analysis_id: int
    candidate_names: List[str]

# ================================================
# RESPONSE MODELS
# ================================================

class CandidateResult(BaseModel):
    """Single candidate analysis result"""
    name: str
    matched_count: int
    missing_count: int
    match_percentage: float
    weighted_score: Optional[float] = None      # Weighted importance score
    total_weighted: Optional[float] = None
    max_weighted: Optional[float] = None
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: Optional[List[str]] = None

class AnalysisStatistics(BaseModel):
    """Statistics from analysis"""
    average_score: float
    most_matched_skill: Optional[str]
    least_matched_skill: Optional[str]
    total_unique_skills: int

class AnalyzeResponse(BaseModel):
    """Response from analysis endpoint"""
    analysis_id: int
    candidates: List[CandidateResult]
    statistics: AnalysisStatistics
    timestamp: datetime = Field(default_factory=datetime.now)

class AnalysisHistory(BaseModel):
    """Single analysis in history"""
    id: int
    job_description: str
    num_resumes: int
    average_score: float
    best_candidate: str
    best_score: int
    created_at: datetime

class HistoryResponse(BaseModel):
    """Response from history endpoint"""
    total: int
    analyses: List[AnalysisHistory]

class ComparisonResult(BaseModel):
    """Comparison between candidates"""
    candidate1: str
    candidate2: str
    matched_skills_both: List[str]
    unique_to_candidate1: List[str]
    unique_to_candidate2: List[str]
    similarity_score: float

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)