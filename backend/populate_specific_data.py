
import os
import random
import csv
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# --- CONSTANTS ---
CONDITIONS = [
    {'name': 'Hypertension', 'chronic': True},
    {'name': 'Type 2 Diabetes', 'chronic': True},
    {'name': 'Asthma', 'chronic': True},
    {'name': 'COPD', 'chronic': True},
    {'name': 'Coronary Artery Disease', 'chronic': True},
    {'name': 'None', 'chronic': False}
]

SYMPTOMS = [
    {'name': 'Chest Pain', 'sevRange': (3, 5), 'duration': '2 hours'},
    {'name': 'Shortness of Breath', 'sevRange': (2, 5), 'duration': '1 day'},
    {'name': 'Severe Headache', 'sevRange': (2, 4), 'duration': '3 days'},
    {'name': 'High Fever', 'sevRange': (3, 5), 'duration': '2 days'},
    {'name': 'Abdominal Pain', 'sevRange': (2, 5), 'duration': '4 hours'},
    {'name': 'Dizziness', 'sevRange': (1, 3), 'duration': 'Morning'},
]

# --- HELPERS ---
def random_date(days_back=365):
    start = datetime.now() - timedelta(days=days_back)
    return start + timedelta(days=random.randint(0, days_back))

def load_and_upload_patients(csv_path="specific_patients.csv"):
    print(f"Loading patients from {csv_path}...")
    try:
        patients = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                patients.append({
                    "patient_id": int(row['patient_id']), 
                    "full_name": row['full_name'],
                    "age": int(row['age']),
                    "gender": row['gender'],
                    "contact_info": row['contact_info']
                })
        
        print(f"Read {len(patients)} patients.")

        # Insert in chunks
        chunk_size = 100
        inserted_ids = []
        
        for i in range(0, len(patients), chunk_size):
            chunk = patients[i:i + chunk_size]
            data, _ = supabase.table("patients").insert(chunk).execute()
            inserted_ids.extend([d['patient_id'] for d in data[1]])
            
        print("Success: User-specific Patients inserted.")
        return inserted_ids
        
    except Exception as e:
        print(f"Error inserting patients: {e}")
        return []

def generate_history(patient_ids):
    print("Generating medical history...")
    # ... (rest of function body)
    history_data = []
    for pid in patient_ids:
        if random.random() > 0.4: # 60% healthy
            cond = random.choice(CONDITIONS)
            if cond['name'] != 'None':
                history_data.append({
                    "patient_id": pid,
                    "condition_name": cond['name'],
                    "is_chronic": cond['chronic'],
                    "notes": "Generated History",
                    "diagnosis_date": str(random_date(1000).date())
                })
    
    if history_data:
        try:
            supabase.table("patient_medical_history").insert(history_data).execute()
            print(f"Success: {len(history_data)} History records inserted.")
        except Exception as e:
            print(f"Error inserting history: {e}")

if __name__ == "__main__":
    # 1. Load User Patients
    pids = load_and_upload_patients("specific_patients.csv")
    
    if pids:
        # 2. Generate Random History for them
        generate_history(pids)
        
        # 3. Generate Specific Visit Counts
        generate_visits_and_predictions(pids, 507)

def run_ml_logic(visit_id, patient_data, symptoms_list):
    # Simplified ML Logic to match backend
    risk_score = 0.1
    dept_scores = {"Emergency": 0.1, "Cardiology": 0.1, "Respiratory": 0.1, "Neurology": 0.1, "General Medicine": 0.2, "Orthopedics": 0.05}
    explainability = {}
    
    # Age Factor
    if patient_data['age'] > 50:
        risk_score += 0.15
        explainability[f"Age {patient_data['age']}"] = 0.15
    
    # Symptom Factor
    for s in symptoms_list:
        name = s['name'].lower()
        score = s['severity']
        
        if "chest pain" in name:
            risk_score += 0.6  # Bump to ensure High Risk (0.1 + 0.6 = 0.7)
            dept_scores["Cardiology"] += 0.6
            dept_scores["Emergency"] += 0.5
        elif "shortness" in name:
            risk_score += 0.4  # Moderate bump
            dept_scores["Respiratory"] += 0.5
            dept_scores["Emergency"] += 0.3
        elif "headache" in name or "dizziness" in name:
            dept_scores["Neurology"] += 0.4
    
    risk_score = min(risk_score, 0.99)
    # Ensure departments match symptom
    target_dept = max(dept_scores, key=dept_scores.get)
    risk_level = "High" if risk_score > 0.66 else "Medium" if risk_score > 0.33 else "Low"
    
    return {
        "visit_id": visit_id,
        "risk_level": risk_level,
        "risk_score": round(risk_score, 2),
        "recommended_department": target_dept,
        "department_scores": dept_scores,
        "explainability": explainability
    }

def generate_visits_and_predictions(patient_ids, count=507):
    print(f"Generating {count} visits and predictions...")
    
    # Get dept map
    depts = supabase.table("departments").select("dept_id, dept_name").execute()
    dept_map = {d['dept_name']: d['dept_id'] for d in depts.data}
    dept_emergency_id = dept_map.get("Emergency")

    # Fetch basic patient data for simulation
    # We need to fetch ALL inserted patients to loop through them
    all_patients = []
    # Fetch in chunks if needed, but 200 is small
    res = supabase.table("patients").select("patient_id, age").execute()
    all_patients = res.data
    
    if not all_patients:
        print("Error: No patients found in DB.")
        return

    # Target 307 High Risk
    high_risk_target = 307
    high_risk_count = 0
    
    for i in range(count):
        # Round robin assign to patients
        p = all_patients[i % len(all_patients)]
        pid = p['patient_id']
        
        # Determine if we want this to be high risk
        force_high_risk = high_risk_count < high_risk_target
        
        if force_high_risk:
            # Force Chest Pain (High Risk Symptom)
            symptom = SYMPTOMS[0] # Chest Pain
            severity = 5
            high_risk_count += 1
        else:
            # Random other symptoms (mostly low/medium)
            symptom = random.choice(SYMPTOMS[1:]) 
            severity = random.randint(symptom['sevRange'][0], symptom['sevRange'][1])
        
        # 1. Create Visit
        v_data, _ = supabase.table("patient_visits").insert({
            "patient_id": pid,
            "chief_complaint": f"{symptom['name']} - Generated",
            "visit_status": "active"
        }).execute()
        vid = v_data[1][0]['visit_id']
        
        # 2. Add Symptoms
        supabase.table("visit_symptoms").insert({
            "visit_id": vid,
            "symptom_name": symptom['name'],
            "severity_score": severity,
            "duration": symptom['duration']
        }).execute()
        
        # 3. Add Vitals (Mock)
        # Higher vitals for high risk
        sys_bp = 160 if force_high_risk else 120
        hr = 110 if force_high_risk else 80
        
        supabase.table("vitals").insert({
            "visit_id": vid,
            "bp_systolic": sys_bp, "bp_diastolic": 80, "heart_rate": 80, "temperature": 98.6
        }).execute()
        
        # 4. Generate Predictions & Queue
        ml_res = run_ml_logic(vid, p, [{'name': symptom['name'], 'severity': severity}])
        
        p_data, _ = supabase.table("triage_predictions").insert(ml_res).execute()
        pred_id = p_data[1][0]['prediction_id']
        
        # 5. Add to Queue
        t_dept = ml_res['recommended_department']
        d_id = dept_map.get(t_dept, dept_emergency_id)
        
        supabase.table("department_queue").insert({
            "prediction_id": pred_id,
            "dept_id": d_id,
            "priority_score": ml_res['risk_score'],
            "status": "pending"
        }).execute()
        
        if i % 50 == 0:
            print(f"Generated {i} records... (High Risk so far: {high_risk_count})")

    print(f"Success: Generated {count} visits with {high_risk_count} High Risk entries from User Patients.")

if __name__ == "__main__":
    # 1. Load User Patients
    pids = load_and_upload_patients("specific_patients.csv")
    
    if pids:
        # 2. Generate Random History for them
        generate_history(pids)
        
        # 3. Generate Specific Visit Counts
        generate_visits_and_predictions(pids, 507)
