
import os
import random
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("Simulating ONE High Risk Patient...")

try:
    # 1. Create Patient
    p_res = supabase.table("patients").insert({
        "full_name": "Critical Patient Demo",
        "age": 65,
        "gender": "Male",
        "contact_info": f"demo_{random.randint(1000,9999)}"
    }).execute()
    pid = p_res.data[0]['patient_id']

    # 2. Create Visit
    v_res = supabase.table("patient_visits").insert({
        "patient_id": pid,
        "chief_complaint": "Severe Chest Pain",
        "visit_status": "active"
    }).execute()
    vid = v_res.data[0]['visit_id']

    # 3. Add Critical Vitals
    supabase.table("vitals").insert({
        "visit_id": vid,
        "bp_systolic": 180,
        "bp_diastolic": 110,
        "heart_rate": 130,
        "temperature": 99.0
    }).execute()

    # 4. Add Symptoms
    supabase.table("visit_symptoms").insert({
        "visit_id": vid,
        "symptom_name": "Chest Pain",
        "severity_score": 5,
        "duration": "1 hour"
    }).execute()

    # 5. Add Triage Prediction (High Risk)
    pred_res = supabase.table("triage_predictions").insert({
        "visit_id": vid,
        "risk_level": "High",
        "risk_score": 0.95,
        "recommended_department": "Cardiology",
        "explainability": {"reason": "Vital signs critical + Chest Pain"}
    }).execute()
    pred_id = pred_res.data[0]['prediction_id']

    # 6. Add to Queue
    supabase.table("department_queue").insert({
        "prediction_id": pred_id,
        "dept_id": 1, # Assuming Emergency or Cardiology exists, usually ID 1 or 2
        "priority_score": 0.95,
        "queue_position": 1,
        "status": "pending"
    }).execute()

    print("✅ High Risk Patient Inserted.")

except Exception as e:
    print(f"❌ Error: {e}")
