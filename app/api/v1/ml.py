from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from app.core.database import Database
from app.models.rule_engine import RuleBasedTriageEngine

router = APIRouter()

class ProcessVisitRequest(BaseModel):
    visit_id: int

class ProcessVisitResponse(BaseModel):
    visit_id: int
    risk_level: str
    risk_score: float
    primary_department: str
    department_scores: Dict[str, float]
    explainability: Dict[str, Any]
    confidence: Dict[str, Any]

@router.post("/process_visit", response_model=ProcessVisitResponse)
async def process_visit(request: ProcessVisitRequest):
    """
    Main endpoint: visit_id → Rule-Based Triage → JSON for main backend
    """
    try:
        # 1. Fetch patient visit data
        visit_data = Database.get_visit_features(request.visit_id)
        
        # 2. Run rule-based triage engine
        triage_engine = RuleBasedTriageEngine()
        prediction = triage_engine.predict(visit_data)
        
        # 3. Return prediction JSON to main backend
        return ProcessVisitResponse(
            visit_id=request.visit_id,
            risk_level=prediction["risk_level"],
            risk_score=prediction["risk_score"],
            primary_department=prediction["primary_department"],
            department_scores=prediction["department_scores"],
            explainability=prediction["explainability"],
            confidence=prediction["confidence"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage prediction failed: {str(e)}")
