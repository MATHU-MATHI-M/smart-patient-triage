
import os
import random
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

supabase = create_client(url, key)

print("Checking full database schema & permissions...")

try:
    # 1. Test Insert Patient
    print("Testing 'patients' INSERT...")
    test_email = f"test_{random.randint(1000,9999)}@example.com"
    data = {
        "full_name": "Test Patient",
        "age": 30,
        "gender": "Male",
        "contact_info": test_email
    }
    res = supabase.table("patients").insert(data).execute()
    new_pid = res.data[0]['patient_id']
    print(f"✅ inserted patient ID: {new_pid}")

    # 2. Test Insert History
    print("Testing 'patient_medical_history' INSERT...")
    h_data = {
        "patient_id": new_pid,
        "condition_name": "Test Condition",
        "is_chronic": False,
        "notes": "Test note",
        "diagnosis_date": "2023-01-01"
    }
    supabase.table("patient_medical_history").insert(h_data).execute()
    print("✅ inserted history")

    # 3. Test Insert Visit
    print("Testing 'patient_visits' INSERT...")
    v_data = {
        "patient_id": new_pid,
        "chief_complaint": "Test complaint",
        "visit_status": "active"
    }
    v_res = supabase.table("patient_visits").insert(v_data).execute()
    new_vid = v_res.data[0]['visit_id']
    print(f"✅ inserted visit ID: {new_vid}")

    # Clean up (optional but good)
    print("Cleaning up test data...")
    supabase.table("patients").delete().eq("patient_id", new_pid).execute()
    print("✅ cleanup done")

except Exception as e:
    print(f"❌ DATABASE ERROR: {e}")
