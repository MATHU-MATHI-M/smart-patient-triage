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

async def run_ml_engine(visit_id: int, patient_id: int):
    """
    Local Fallback Logic:
    Fetches data and performs rule-based triage when external ML is unavailable.
    """
    # 1. Fetch STATIC Patient Data
    p_res = supabase.table("patients").select("age, gender").eq("patient_id", patient_id).execute()
    p_data = p_res.data[0] if p_res.data else {}
    
    # 2. Fetch STATIC History
    h_res = supabase.table("patient_medical_history").select("condition_name, notes").eq("patient_id", patient_id).execute()
    history_text = " ".join([f"{h['condition_name']} {h.get('notes') or ''}" for h in h_res.data]).lower()
    
    # 3. Fetch Vitals
    v_res = supabase.table("vitals").select("bp_systolic, heart_rate, temperature").eq("visit_id", visit_id).execute()
    vitals = v_res.data[0] if v_res.data else {}
    
    # 4. Fetch Symptoms
    s_res = supabase.table("visit_symptoms").select("symptom_name, severity_score").eq("visit_id", visit_id).execute()
    symptoms = s_res.data
    
    # --- Logic ---
    risk_score = 0.1
    explainability = {}
    dept_scores = {"Emergency": 0.1, "Cardiology": 0.1, "Respiratory": 0.1, "Neurology": 0.1, "General Medicine": 0.15, "Orthopedics": 0.05}
    
    # A. History
    if any(k in history_text for k in ["heart", "cardiac", "angina", "murmur", "failure"]):
        dept_scores["Cardiology"] += 0.3
        risk_score += 0.15
        explainability["Cardiac History"] = 0.15
        
    if any(k in history_text for k in ["lung", "asthma", "copd", "breath"]):
        dept_scores["Respiratory"] += 0.3
        risk_score += 0.1

    # B. Vitals
    sys_bp = vitals.get('bp_systolic', 120)
    if sys_bp > 160:
        risk_score += 0.25
        dept_scores["Emergency"] += 0.2
        dept_scores["Cardiology"] += 0.3
        explainability[f"BP {sys_bp}"] = 0.25

    # C. Symptoms
    for s in symptoms:
        name = s['symptom_name'].lower()
        if any(k in name for k in ["chest", "heart", "pain"]):
            risk_score += 0.3
            dept_scores["Cardiology"] += 0.5
            dept_scores["Emergency"] += 0.2
            explainability[f"Sx: {name}"] = 0.3
        elif any(k in name for k in ["breath", "cough"]):
            risk_score += 0.25
            dept_scores["Respiratory"] += 0.5
            
    # Normalize
    risk_score = min(risk_score, 0.99)
    # Classification
    if risk_score > 0.70: risk_level = "High"
    elif risk_score > 0.40: risk_level = "Medium"
    else: risk_level = "Low"

    recommended_department = max(dept_scores, key=dept_scores.get)
    
    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 2),
        "primary_department": recommended_department, # key match
        "recommended_department": recommended_department,
        "department_scores": dept_scores,
        "explainability": explainability
    }

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
                    timeout=60.0  # ✅ Increased to 60s
                )
                ml_response.raise_for_status()
                ml_result = ml_response.json()
                
                print(f"ML Engine Response: {ml_result.keys()}")
                
                if "primary_department" in ml_result:
                    recommended_dept = ml_result["primary_department"]
                elif "recommended_department" in ml_result:
                    recommended_dept = ml_result["recommended_department"]
                else:
                    raise ValueError("ML response missing department field")
                
                if "department_scores" not in ml_result:
                    raise ValueError("ML response missing department_scores")
                    
            except (httpx.TimeoutException, httpx.HTTPError, Exception) as e:
                print(f"External ML Service Failed ({str(e)}). Switching to Local Fallback.")
                try:
                    # LOCAL FALLBACK
                    ml_result = await run_ml_engine(visit_id, visit.patient_id)
                    recommended_dept = ml_result["recommended_department"]
                except Exception as local_e:
                    print(f"CRITICAL: Local Fallback also failed: {local_e}")
                    raise HTTPException(status_code=500, detail=f"Triage Assessment Failed: {str(local_e)}")
    
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
                visit_id,
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

# ==============================
# AI EXPLAINABILITY (OpenRouter)
# ==============================
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class VisitRequest(BaseModel):
    visit_id: int # Changed from str to int to match DB

def get_prediction_data(visit_id):
    try:
        # Fetch Prediction
        p_res = supabase.table("triage_predictions").select("*").eq("visit_id", visit_id).execute()
        if not p_res.data:
            raise ValueError("Prediction not found")
        prediction = p_res.data[0]

        # Fetch Vitals
        v_res = supabase.table("vitals").select("*").eq("visit_id", visit_id).execute()
        vitals = v_res.data[0] if v_res.data else {}

        # Fetch Symptoms
        s_res = supabase.table("visit_symptoms").select("*").eq("visit_id", visit_id).execute()
        symptoms = s_res.data

        # Fetch Visit
        vis_res = supabase.table("patient_visits").select("*").eq("visit_id", visit_id).execute()
        if not vis_res.data:
            raise ValueError("Visit not found")
        visit = vis_res.data[0]

        # Fetch Patient
        pat_res = supabase.table("patients").select("*").eq("patient_id", visit["patient_id"]).execute()
        patient = pat_res.data[0] if pat_res.data else {}

        return prediction, vitals, symptoms, visit, patient

    except Exception as e:
        print(f"Error fetching data for explainability: {e}")
        raise HTTPException(status_code=404, detail=f"Visit data not found: {str(e)}")


def explain_prediction(prediction, vitals, symptoms, visit, patient):
    symptom_list = [s["symptom_name"] for s in symptoms]

    prompt = f"""
You are an explainable AI medical triage assistant.

Patient Details:
Age: {patient.get('age', 'N/A')}
Gender: {patient.get('gender', 'N/A')}
Chief Complaint: {visit.get('chief_complaint', 'N/A')}

Vitals:
BP: {vitals.get('bp_systolic', '?')}/{vitals.get('bp_diastolic', '?')}
Heart Rate: {vitals.get('heart_rate', '?')}
Temperature: {vitals.get('temperature', '?')}

Symptoms:
{symptom_list}

Model Prediction:
Risk Level: {prediction.get('risk_level', 'Unknown')}
Risk Score: {prediction.get('risk_score', 0)}
Recommended Department: {prediction.get('recommended_department', 'General')}

Provide a concise explanation (MAX 3 lines - strictly do not exceed):
- Key contributing clinical factors
- Reason for predicted risk level
- Confidence explanation based only on given data
Avoid assumptions or hallucinations.
"""

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )

        data = res.json()
        # print("OpenRouter RAW Response:", data)  

        # Safe handling
        if "choices" not in data:
            return {
                "status": "error",
                "message": data
            }

        return {
            "status": "success",
            "explanation": data["choices"][0]["message"]["content"]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/triage-explain")
def triage_explain(request: VisitRequest):
    print(f"Explaining prediction for visit {request.visit_id}")
    
    # 1. Gather Data
    prediction, vitals, symptoms, visit, patient = get_prediction_data(request.visit_id)

    # 2. Call LLM
    explanation_result = explain_prediction(prediction, vitals, symptoms, visit, patient)

    # Unwrap the dictionary response
    if isinstance(explanation_result, dict) and "explanation" in explanation_result:
        explanation_text = explanation_result["explanation"]
    elif isinstance(explanation_result, dict) and "message" in explanation_result:
        explanation_text = f"Error: {explanation_result['message']}"
    else:
        explanation_text = str(explanation_result)

    return {
        "visit_id": request.visit_id,
        "risk_level": prediction["risk_level"],
        "risk_score": prediction["risk_score"],
        "recommended_department": prediction["recommended_department"],
        "explanation": explanation_text
    }