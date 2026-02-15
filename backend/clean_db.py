import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("Error: Missing credentials")
    exit(1)

supabase = create_client(url, key)

print("Deleting all data...")
try:
    # Delete all patients (ID > 0)
    # This cascades to history, visits, vitals, symptoms, predictions
    res = supabase.table("patients").delete().gt("patient_id", 0).execute()
    count = len(res.data) if res.data else 0
    print(f"Deleted {count} patients and all related records.")
except Exception as e:
    print(f"Error: {e}")
