from fastapi import APIRouter, HTTPException, Query
from backend.database import get_all_analyses, get_analysis_with_candidates, delete_analysis, search_analyses
from backend.models import HistoryResponse, AnalysisHistory
from typing import List

router = APIRouter(prefix="/api", tags=["History"])

@router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Get analysis history
    
    Args:
        limit: Number of records to return
        skip: Number of records to skip
    
    Returns:
        List of past analyses
    """
    try:
        analyses = get_all_analyses(limit=limit)
        
        # Apply skip
        analyses = analyses[skip:skip + limit]
        
        history_items = [
            AnalysisHistory(
                id=a['id'],
                job_description=a['job_description'][:100] + ('...' if len(a['job_description']) > 100 else ''),
                num_resumes=a['num_resumes'],
                average_score=a['average_score'],
                best_candidate=a['best_candidate'],
                best_score=a['best_score'],
                created_at=a['created_at']
            )
            for a in analyses
        ]
        
        return HistoryResponse(
            total=len(analyses),
            analyses=history_items
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@router.get("/history/{analysis_id}")
async def get_analysis_details(analysis_id: int):
    """
    Get specific analysis with all candidates
    
    Args:
        analysis_id: Analysis ID
    
    Returns:
        Detailed analysis with candidates
    """
    try:
        result = get_analysis_with_candidates(analysis_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analysis: {str(e)}")

@router.delete("/history/{analysis_id}")
async def delete_history(analysis_id: int):
    """
    Delete an analysis from history
    
    Args:
        analysis_id: Analysis ID to delete
    
    Returns:
        Success message
    """
    try:
        success = delete_analysis(analysis_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {"message": "Analysis deleted successfully", "analysis_id": analysis_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete analysis: {str(e)}")

@router.get("/history/search/{query}")
async def search_history(query: str):
    """
    Search analysis history
    
    Args:
        query: Search query (candidate name or skill)
    
    Returns:
        Matching analyses
    """
    try:
        if len(query) < 2:
            raise HTTPException(status_code=400, detail="Search query too short")
        
        results = search_analyses(query)
        
        history_items = [
            AnalysisHistory(
                id=a['id'],
                job_description=a['job_description'][:100],
                num_resumes=a['num_resumes'],
                average_score=a['average_score'],
                best_candidate=a['best_candidate'],
                best_score=a['best_score'],
                created_at=a['created_at']
            )
            for a in results
        ]
        
        return HistoryResponse(
            total=len(history_items),
            analyses=history_items
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")