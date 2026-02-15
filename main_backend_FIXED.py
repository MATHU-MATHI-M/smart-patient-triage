"""
CORRECTED Main Backend - Fixed Queue Routing
This version properly integrates with the ML backend API
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError
from pydantic import BaseModel
from supabase import create_client, Client
import os
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Triage Data API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://0.0.0.0:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Triage API is running", "status": "ok"}

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@app.exception_handler(APIError)
async def postgrest_exception_handler(request: Request, exc: APIError):
    details = exc.args[0] if exc.args else {}
    if isinstance(details, dict) and details.get("code") == "PGRST205":
        return JSONResponse(
            status_code=500,
            content={"detail": "CRITICAL: Database tables missing. Please run setup_database.sql in Supabase SQL Editor."},
        )
    print(f"PostgREST Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Database Error: {exc}"},
    )

# Models
class MedicalHistory(BaseModel):
    condition_name: str
    is_chronic: bool
    notes: str = None
    diagnosis_date: str = None

class PatientInput(BaseModel):
    full_name: str
    age: int
    gender: str
    contact_info: str = None
    medical_history: List[MedicalHistory] = []

class SymptomInput(BaseModel):
    symptom_name: str
    severity_score: int
    duration: str

class VisitInput(BaseModel):
    patient_id: int
    chief_complaint: str
    bp_systolic: int
    bp_diastolic: int
    heart_rate: int
    temperature: float
    symptoms: List[SymptomInput]

@app.get("/patients/lookup")
async def lookup_patient(id: int = None, name: str = None, email: str = None):
    """Search patient by ID, Name, or Email"""
    query = supabase.table("patients").select("*")
    
    if id:
        query = query.eq("patient_id", id)
    else:
        if name:
            query = query.ilike("full_name", f"%{name}%")
        if email:
            query = query.eq("contact_info", email)
            
    result = query.limit(5).execute()
    return {"patients": result.data}

@app.get("/patients/{patient_id}/history")
async def get_patient_history(patient_id: int):
    """Get patient medical history"""
    result = supabase.table("patient_medical_history").select("*").eq("patient_id", patient_id).execute()
    return {"history": result.data}

@app.post("/patients/{patient_id}/history")
async def add_history(patient_id: int, history: List[MedicalHistory]):
    """Add history items to existing patient"""
    if history:
        hist_data = [
            {
                "patient_id": patient_id, 
                "condition_name": h.condition_name, 
                "is_chronic": h.is_chronic,
                "notes": h.notes,
                "diagnosis_date": h.diagnosis_date
            } for h in history
        ]
        supabase.table("patient_medical_history").insert(hist_data).execute()
    return {"message": "History added"}

@app.post("/patients")
async def create_patient(patient: PatientInput):
    """Create new patient with initial history"""
    p_data, _ = supabase.table("patients").insert({
        "full_name": patient.full_name,
        "age": patient.age,
        "gender": patient.gender,
        "contact_info": patient.contact_info
    }).execute()
    
    new_pid = p_data[1][0]["patient_id"] 
    
    if patient.medical_history:
        hist_data = [
            {
                "patient_id": new_pid, 
                "condition_name": h.condition_name, 
                "is_chronic": h.is_chronic,
                "notes": h.notes,
                "diagnosis_date": h.diagnosis_date
            } for h in patient.medical_history
        ]
        supabase.table("patient_medical_history").insert(hist_data).execute()

    return {"patient_id": new_pid, "message": "Patient created"}

@app.post("/patient-visits")
async def create_visit(visit: VisitInput):
    """
    Create visit + trigger ML pipeline
    
    FIXED VERSION:
    - Increased API timeout to 30s (handles cold starts)
    - Removed flawed local fallback
    - Proper error handling
    - Standardized response keys
    """
    print(f"Received Visit: {visit.patient_id} - {visit.chief_complaint}")
    try:
        # 1. Insert Visit
        v_data, _ = supabase.table("patient_visits").insert({
            "patient_id": visit.patient_id,
            "chief_complaint": visit.chief_complaint,
            "visit_status": "active"
        }).execute()
        
        visit_id = v_data[1][0]["visit_id"]
        
        # 2. Insert Vitals
        supabase.table("vitals").insert({
            "visit_id": visit_id,
            "bp_systolic": visit.bp_systolic,
            "bp_diastolic": visit.bp_diastolic,
            "heart_rate": visit.heart_rate,
            "temperature": visit.temperature
        }).execute()
        
        # 3. Insert Symptoms
        if visit.symptoms:
            s_data = [
                {
                    "visit_id": visit_id, 
                    "symptom_name": s.symptom_name,
                    "severity_score": min(max(s.severity_score, 1), 5),
                    "duration": s.duration
                } for s in visit.symptoms
            ]
            supabase.table("visit_symptoms").insert(s_data).execute()
        
        # 4. ✅ FIXED: Call ML Engine with proper timeout and error handling
        async with httpx.AsyncClient() as client:
            try:
                print(f"Calling ML Engine for visit {visit_id}...")
                ml_response = await client.post(
                    "https://ml-backend-engine-kanini.onrender.com/api/v1/process_visit",
                    json={"visit_id": visit_id},
                    timeout=30.0  # ✅ FIXED: Increased from 5s to 30s for cold starts
                )
                ml_response.raise_for_status()
                ml_result = ml_response.json()
                
                print(f"ML Engine Response: {ml_result.keys()}")
                
                # ✅ FIXED: Handle both response formats
                # Rule-based engine returns: primary_department
                # Old ML engine might return: recommended_department
                if "primary_department" in ml_result:
                    recommended_dept = ml_result["primary_department"]
                elif "recommended_department" in ml_result:
                    recommended_dept = ml_result["recommended_department"]
                else:
                    raise ValueError("ML response missing department field")
                
                # Validate required fields
                if "department_scores" not in ml_result:
                    raise ValueError("ML response missing department_scores")
                    
            except httpx.TimeoutException:
                print("ML Engine timeout - service may be cold starting")
                raise HTTPException(
                    status_code=503, 
                    detail="ML Engine is starting up. Please try again in 10 seconds."
                )
            except httpx.HTTPError as e:
                print(f"ML Engine HTTP error: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=f"ML Engine unavailable: {str(e)}"
                )
            except Exception as e:
                print(f"ML Engine error: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Triage assessment failed: {str(e)}"
                )
    
        # 5. Insert Predictions
        pred_data, _ = supabase.table("triage_predictions").insert({
            "visit_id": visit_id,
            "risk_level": ml_result["risk_level"],
            "risk_score": ml_result["risk_score"],
            "recommended_department": recommended_dept,  # ✅ FIXED: Use standardized key
            "department_scores": ml_result["department_scores"],
            "explainability": ml_result.get("explainability", {})
        }).execute()
        
        pred_id = pred_data[1][0]["prediction_id"]
    
        # 6. ✅ Multi-Department Queue Routing (Already Correct!)
        threshold = 0.35  # Queue threshold
        queued_depts = []
        
        print(f"Department Scores: {ml_result['department_scores']}")
        
        # Add to all departments with score >= threshold
        for dept, score in ml_result["department_scores"].items():
            if score >= threshold:
                d_res = supabase.table("departments").select("dept_id").eq("dept_name", dept).execute()
                if d_res.data:
                    d_id = d_res.data[0]['dept_id']
                    supabase.table("department_queue").insert({
                        "prediction_id": pred_id,
                        "dept_id": d_id,
                        "priority_score": score, 
                        "status": "pending"
                    }).execute()
                    queued_depts.append(f"{dept}({score:.2f})")
                    print(f"✅ Queued to {dept} with priority {score:.2f}")

        # Safety fallback: If no department met threshold, queue to primary
        if not queued_depts:
            dept_res = supabase.table("departments").select("dept_id").eq("dept_name", recommended_dept).execute()
            
            if not dept_res.data:
                dept_res = supabase.table("departments").select("dept_id").eq("dept_name", "Emergency").execute()
                 
            if dept_res.data:
                d_id = dept_res.data[0]['dept_id']
                supabase.table("department_queue").insert({
                    "prediction_id": pred_id,
                    "dept_id": d_id,
                    "priority_score": ml_result["department_scores"].get(recommended_dept, ml_result["risk_score"]), 
                    "status": "pending"
                }).execute()
                queued_depts.append(f"{recommended_dept}(fallback)")
        
        print(f"✅ Visit {visit_id} queued to: {', '.join(queued_depts)}")
        
        return {
            "visit_id": visit_id, 
            "message": "Visit created, ML Analysis Complete",
            "queued_departments": queued_depts
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        print(f"CRITICAL ERROR in create_visit: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing Error: {str(e)}")

@app.patch("/queue/{queue_id}/status")
async def update_queue_status(queue_id: int, status: str):
    """Update patient status"""
    allowed_statuses = ["pending", "treating", "completed", "discharged", "referred"]
    
    s_norm = status.lower().strip()
    
    if s_norm in ["completed", "discharged"]:
        q_res = supabase.table("department_queue").select("prediction_id").eq("queue_id", queue_id).execute()
        if q_res.data:
            pred_id = q_res.data[0]['prediction_id']
            
            p_res = supabase.table("triage_predictions").select("visit_id").eq("prediction_id", pred_id).execute()
            if p_res.data:
                visit_id = p_res.data[0]['visit_id']
                supabase.table("patient_visits").update({"visit_status": "completed"}).eq("visit_id", visit_id).execute()

        data, _ = supabase.table("department_queue").delete().eq("queue_id", queue_id).execute()
        return {"message": "Patient discharged and removed from queue", "data": data}

    else:
        data, _ = supabase.table("department_queue").update({"status": s_norm}).eq("queue_id", queue_id).execute()
        return {"message": "Status updated", "data": data}

@app.get("/queues/{dept_name}")
async def get_queue(dept_name: str):
    """Get active queue for department"""
    d_res = supabase.table("departments").select("dept_id").eq("dept_name", dept_name).execute()
    if not d_res.data:
        return {"queue": []}
        
    dept_id = d_res.data[0]['dept_id']
    
    result = supabase.table("department_queue").select("""
        *,
        triage_predictions!inner(
            risk_score, 
            risk_level, 
            patient_visits!inner(
                visit_timestamp, 
                chief_complaint, 
                patients!inner(full_name, age, gender, contact_info)
            )
        )
    """).eq("dept_id", dept_id).neq("status", "completed").neq("status", "discharged").order("priority_score", desc=True).limit(50).execute()
    
    return {"queue": result.data}

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get high-level hospital stats"""
    total_p = supabase.table("patients").select("patient_id", count="exact").execute()
    
    active_q_res = supabase.table("department_queue").select("""
        prediction_id,
        status,
        triage_predictions!inner(
            risk_level,
            patient_visits!inner(visit_timestamp)
        )
    """).in_("status", ["pending", "treating"]).execute()
    
    active_items = active_q_res.data
    unique_active_preds = {}
    
    avg_wait = 0
    total_seconds = 0
    valid_wait_times = 0

    if active_items:
        try:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            
            for item in active_items:
                pred_id = item['prediction_id']
                
                if pred_id not in unique_active_preds:
                    unique_active_preds[pred_id] = {
                        "risk_level": item['triage_predictions'].get('risk_level', 'Low')
                    }
                    
                    try:
                        ts_str = item['triage_predictions']['patient_visits']['visit_timestamp']
                        if ts_str.endswith('Z'):
                            ts_str = ts_str.replace('Z', '+00:00')
                        visit_time = datetime.fromisoformat(ts_str)
                        if visit_time.tzinfo is None:
                            visit_time = visit_time.replace(tzinfo=timezone.utc)
                        
                        diff = now - visit_time
                        wait_secs = max(0, diff.total_seconds())
                        total_seconds += wait_secs
                        valid_wait_times += 1
                        
                    except Exception:
                        pass
                
        except Exception as e:
            print(f"Error calculating stats: {e}")

    high_count = 0
    medium_count = 0
    low_count = 0
    
    for pid, data in unique_active_preds.items():
        if data['risk_level'] == 'High':
            high_count += 1
        elif data['risk_level'] == 'Medium':
            medium_count += 1
        else:
            low_count += 1

    active_count = len(unique_active_preds)
    
    if valid_wait_times > 0:
        avg_wait = int((total_seconds / valid_wait_times) / 60)
    
    return {
        "total_patients": total_p.count,
        "active_visits": active_count,
        "high_risk_patients": high_count,
        "medium_risk_patients": medium_count, 
        "low_risk_patients": low_count,
        "avg_wait_time": avg_wait
    }
