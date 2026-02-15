
import os
import time
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

TABLES = [
    {"name": "patients", "pk": "patient_id", "dummy": {"full_name": "FIX", "age": 0}},
    {"name": "patient_medical_history", "pk": "history_id", "dummy": {"condition_name": "FIX"}}, 
    {"name": "patient_visits", "pk": "visit_id", "dummy": {"chief_complaint": "FIX", "visit_status": "fix"}},
    {"name": "vitals", "pk": "vitals_id", "dummy": {"bp_systolic": 0}},
    {"name": "visit_symptoms", "pk": "symptom_id", "dummy": {"symptom_name": "FIX", "severity_score": 1}},
    {"name": "triage_predictions", "pk": "prediction_id", "dummy": {"risk_score": 0.0}},
    {"name": "department_queue", "pk": "queue_id", "dummy": {"status": "fix"}},
]

print("Starting FULL Database Sequence Repair...")

for t in TABLES:
    print(f"\nScanning table: {t['name']}...")
    try:
        # Get Max ID
        res = supabase.table(t['name']).select(t['pk']).order(t['pk'], desc=True).limit(1).execute()
        
        max_id = 0
        if res.data:
            max_id = res.data[0][t['pk']]
        
        print(f"  Current MAX {t['pk']}: {max_id}")
        
        # Determine strict constraints (we need valid FKs for some tables to insert dummy rows)
        # This is tricky without knowing valid FKs.
        # However, backend logic usually handles `init_db.py` seeding for departments.
        # But `patient_visits` needs valid `patient_id`.
        
        # Strategy: Use existing Max ID + 1? No, we can't force ID insert readily unless we enable identity insert.
        # PostgREST doesn't support forcing ID easily.
        
        # Attempt minimal insert
        # For tables with NOT NULL FKs, we must provide valid FK or we can't insert.
        # Let's see setup_database.sql:
        # patient_medical_history -> patient_id (REFERENCES patients)
        # patient_visits -> patient_id (REFERENCES patients)
        # vitals -> visit_id
        # visit_symptoms -> visit_id
        # triage_predictions -> visit_id
        # department_queue -> prediction_id, dept_id
        
        # We need a valid patient_id (use max_id of patients) and valid visit_id.
        latest_pid = supabase.table("patients").select("patient_id").order("patient_id", desc=True).limit(1).execute().data[0]['patient_id']
        
        # Prepare dummy data
        data = t['dummy'].copy()
        if "patient_id" in [c.name for c in  supabase.table(t['name']).select("*").limit(0).execute().data]: # Hacky check? No.
             pass
        
        # Manual mapping for FKs
        if t['name'] == "patient_medical_history":
            data['patient_id'] = latest_pid
        elif t['name'] == "patient_visits":
            data['patient_id'] = latest_pid
            
        # For visits dependent tables, get a valid visit_id
        if t['name'] in ["vitals", "visit_symptoms", "triage_predictions"]:
            latest_vid = supabase.table("patient_visits").select("visit_id").order("visit_id", desc=True).limit(1).execute().data[0]['visit_id']
            data['visit_id'] = latest_vid
            
        if t['name'] == "department_queue":
            latest_pred = supabase.table("triage_predictions").select("prediction_id").order("prediction_id", desc=True).limit(1).execute().data[0]['prediction_id']
            latest_dept = supabase.table("departments").select("dept_id").limit(1).execute().data[0]['dept_id']
            data['prediction_id'] = latest_pred
            data['dept_id'] = latest_dept

        # Loop to fix sequence
        attempts = 0
        while True:
            attempts += 1
            try:
                ins = supabase.table(t['name']).insert(data).execute()
                new_id = ins.data[0][t['pk']]
                
                # Cleanup
                supabase.table(t['name']).delete().eq(t['pk'], new_id).execute()
                
                if new_id > max_id:
                     print(f"  ✅ Fixed {t['name']}. Next {t['pk']} > {max_id}")
                     break
            except Exception as e:
                if "already exists" in str(e):
                    if attempts % 10 == 0: print(f"  Skipping... {attempts}")
                    continue
                else: 
                     print(f"  ❌ Error fixing {t['name']}: {e}")
                     break
                     
    except Exception as e:
        print(f"  ❌ Global Error on {t['name']}: {e}")

print("\nDone.")
