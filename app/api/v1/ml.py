from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from app.core.database import Database
from app.models.ml_engine import MLEngine

router = APIRouter()

class ProcessVisitRequest(BaseModel):
    visit_id: int

class ProcessVisitResponse(BaseModel):
    visit_id: int
    risk_level: str
    risk_score: float
    primary_department: str  # Maps to recommended_department in DB
    department_scores: Dict[str, float]
    explainability: Dict[str, float]

@router.post("/process_visit", response_model=ProcessVisitResponse)
async def process_visit(request: ProcessVisitRequest):
    """
    Main endpoint: visit_id → ML prediction → JSON for main backend
    """
    try:
        # 1. Fetch patient visit data
        visit_features = Database.get_visit_features(request.visit_id)
        
        # 2. Run ML pipeline
        ml_engine = MLEngine()
        prediction = ml_engine.predict(visit_features)
        
        # 3. Return prediction JSON to main backend
        # Main backend will save to triage_predictions table
        
        return ProcessVisitResponse(
            visit_id=request.visit_id,
            risk_level=prediction["risk_level"],
            risk_score=prediction["risk_score"],
            primary_department=prediction["primary_department"],
            department_scores=prediction["department_scores"],
            explainability=prediction["explainability"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML prediction failed: {str(e)}")
