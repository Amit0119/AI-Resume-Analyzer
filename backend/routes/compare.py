from fastapi import APIRouter, HTTPException
from backend.utils import calculate_similarity
from backend.database import get_analysis_with_candidates
from backend.models import CompareRequest, ComparisonResult
from typing import List

router = APIRouter(prefix="/api", tags=["Comparison"])

@router.post("/compare", response_model=List[ComparisonResult])
async def compare_candidates(request: CompareRequest):
    """
    Compare skills between candidates
    
    Args:
        request: CompareRequest with analysis_id and candidate names
    
    Returns:
        Comparison results
    """
    try:
        # Get analysis with candidates
        analysis_data = get_analysis_with_candidates(request.analysis_id)
        
        if not analysis_data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        candidates = analysis_data['candidates']
        
        # Validate candidate names
        available_names = {c['name'] for c in candidates}
        for name in request.candidate_names:
            if name not in available_names:
                raise HTTPException(status_code=400, detail=f"Candidate '{name}' not found in this analysis")
        
        # Get selected candidates
        selected_candidates = [c for c in candidates if c['name'] in request.candidate_names]
        
        if len(selected_candidates) < 2:
            raise HTTPException(status_code=400, detail="Please select at least 2 candidates to compare")
        
        comparisons = []
        
        # Compare each pair
        for i in range(len(selected_candidates)):
            for j in range(i + 1, len(selected_candidates)):
                c1 = selected_candidates[i]
                c2 = selected_candidates[j]
                
                skills1 = set(c1['matched_skills'])
                skills2 = set(c2['matched_skills'])
                
                # Calculate overlaps
                matched_both = list(skills1 & skills2)
                unique_to_c1 = list(skills1 - skills2)
                unique_to_c2 = list(skills2 - skills1)
                
                # Calculate similarity
                similarity = calculate_similarity(
                    c1['matched_skills'],
                    c2['matched_skills']
                )
                
                comparisons.append(
                    ComparisonResult(
                        candidate1=c1['name'],
                        candidate2=c2['name'],
                        matched_skills_both=matched_both,
                        unique_to_candidate1=unique_to_c1,
                        unique_to_candidate2=unique_to_c2,
                        similarity_score=round(similarity, 2)
                    )
                )
        
        return comparisons
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@router.get("/compare/{analysis_id}/all")
async def compare_all_candidates(analysis_id: int):
    """
    Get comparison summary for all candidates in an analysis
    
    Args:
        analysis_id: Analysis ID
    
    Returns:
        Summary comparison data
    """
    try:
        analysis_data = get_analysis_with_candidates(analysis_id)
        
        if not analysis_data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        candidates = analysis_data['candidates']
        
        if len(candidates) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 candidates to compare")
        
        # Calculate pairwise comparisons
        summary = {
            "total_candidates": len(candidates),
            "comparisons": []
        }
        
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                c1 = candidates[i]
                c2 = candidates[j]
                
                similarity = calculate_similarity(
                    c1['matched_skills'],
                    c2['matched_skills']
                )
                
                summary["comparisons"].append({
                    "candidate1": c1['name'],
                    "candidate2": c2['name'],
                    "similarity_score": round(similarity, 2),
                    "c1_score": f"{c1['matched_count']}/15",
                    "c2_score": f"{c2['matched_count']}/15"
                })
        
        # Sort by similarity
        summary["comparisons"].sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")