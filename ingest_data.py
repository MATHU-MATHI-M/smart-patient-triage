import requests
import json
import os
from dotenv import load_dotenv

# Load key from backend/.env explicitly to check if script can run (but script uses requests to API)
load_dotenv("../backend/.env")

API_URL = "http://localhost:8000"

def ingest_data():
    print("Starting Data Ingestion...")
    print("NOTE: Ensure backend (uvicorn) is restarted to load new keys!")

    # --- PATIENT 1: John Doe (New Patient) ---
    print("\nProcessing Patient 1: John Doe (New)...")
    
    # 1. Create Patient + History
    p1_payload = {
        "full_name": "John Doe",
        "age": 45,
        "gender": "M",
        "contact_info": "john.doe@email.com",
        "medical_history": [
            {"condition_name": "Diabetes", "is_chronic": True, "notes": "Type 2, controlled"},
            {"condition_name": "Hypertension", "is_chronic": True, "notes": "Meds compliant"}
        ]
    }
    
    resp1 = requests.post(f"{API_URL}/patients", json=p1_payload)
    if resp1.status_code == 200:
        p1_id = resp1.json()["patient_id"]
        print(f"Patient Created: John Doe (ID: {p1_id})")
        
        # 2. Create Visit
        v1_payload = {
            "patient_id": p1_id,
            "chief_complaint": "Chest pain for 2 hours",
            "bp_systolic": 160,
            "bp_diastolic": 100,
            "heart_rate": 120,
            "temperature": 99.2,
            "symptoms": [
                {"symptom_name": "chest pain", "severity_score": 4, "duration": "2 hours"},
                {"symptom_name": "shortness of breath", "severity_score": 3, "duration": "1 hour"},
                {"symptom_name": "nausea", "severity_score": 2, "duration": "30 min"}
            ]
        }
        
        v1_resp = requests.post(f"{API_URL}/patient-visits", json=v1_payload)
        if v1_resp.status_code == 200:
            print(f"Visit Created for John Doe (ID: {v1_resp.json()['visit_id']})")
        else:
            print(f"Failed to create visit for John Doe: {v1_resp.text}")
    else:
        print(f"Failed to create John Doe (might exist): {resp1.text}")

    # --- PATIENT 2: Mary Smith (Returning Patient) ---
    print("\nProcessing Patient 2: Mary Smith (Returning)...")
    
    # 1. Check if exists
    search_resp = requests.get(f"{API_URL}/patients/lookup?name=Mary Smith")
    mary_id = None
    
    if search_resp.status_code == 200 and search_resp.json()["patients"]:
        # Found existing
        mary_data = search_resp.json()["patients"][0]
        mary_id = mary_data["patient_id"]
        print(f"Found Existing Patient: Mary Smith (ID: {mary_id})")
        
        # --- NEW: Ensure History Exists ---
        # Fetch current history
        h_resp = requests.get(f"{API_URL}/patients/{mary_id}/history")
        current_history = h_resp.json().get("history", []) if h_resp.status_code == 200 else []
        
        if not current_history:
            print("Adding missing history for Mary Smith...")
            # Add History via new endpoint
            h_payload = [
                {"condition_name": "COPD", "is_chronic": True, "notes": "Oxygen dependent"},
                {"condition_name": "Atrial Fibrillation", "is_chronic": True, "notes": "On blood thinners"}
            ]
            add_h_resp = requests.post(f"{API_URL}/patients/{mary_id}/history", json=h_payload)
            if add_h_resp.status_code == 200:
                print("History added successfully.")
            else:
                print(f"Failed to add history: {add_h_resp.text}")
        else:
            print("History already present:")
            for h in current_history:
                print(f" - {h['condition_name']} (Chronic: {h['is_chronic']})")
            
    else:
        # Not found, create her base record
        print("Mary Smith not found, creating base record first...")
        p2_payload = {
            "full_name": "Mary Smith",
            "age": 62,
            "gender": "F",
            "contact_info": "mary.smith@email.com",
            "medical_history": [
                {"condition_name": "COPD", "is_chronic": True, "notes": "Oxygen dependent"},
                {"condition_name": "Atrial Fibrillation", "is_chronic": True, "notes": "On blood thinners"}
            ]
        }
        resp2 = requests.post(f"{API_URL}/patients", json=p2_payload)
        if resp2.status_code == 200:
            mary_id = resp2.json()["patient_id"]
            print(f"Created Base Record for Mary Smith (ID: {mary_id})")

    if mary_id:
        # 2. Create NEW Visit (Manual Input Only)
        v2_payload = {
            "patient_id": mary_id,
            "chief_complaint": "Worsening shortness of breath since morning",
            "bp_systolic": 150,
            "bp_diastolic": 90,
            "heart_rate": 110,
            "temperature": 100.4,
            "symptoms": [
                {"symptom_name": "shortness of breath", "severity_score": 5, "duration": "6 hours"},
                {"symptom_name": "cough", "severity_score": 4, "duration": "2 days"},
                {"symptom_name": "wheezing", "severity_score": 3, "duration": "6 hours"}
            ]
        }
        
        v2_resp = requests.post(f"{API_URL}/patient-visits", json=v2_payload)
        if v2_resp.status_code == 200:
            print(f"Visit Created for Mary Smith (ID: {v2_resp.json()['visit_id']})") 
        else:
             print(f"Failed to create visit for Mary Smith: {v2_resp.text}")

    print("\nIngestion Complete.")

if __name__ == "__main__":
    ingest_data()
