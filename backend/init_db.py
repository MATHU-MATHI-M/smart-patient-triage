
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env")
    exit(1)

supabase = create_client(url, key)

print("Checking database connection...")

try:
    # 1. Check Patients
    print("Checking 'patients' table...")
    res = supabase.table("patients").select("count", count="exact").limit(1).execute()
    print(f"✅ 'patients' table exists. Count: {res.count}")
except Exception as e:
    print(f"❌ 'patients' table Error: {e}")

try:
    # 2. Check Departments
    print("Checking 'departments' table...")
    res = supabase.table("departments").select("*").execute()
    if not res.data:
        print("⚠️ 'departments' table is EMPTY. Attempting to seed...")
        # Seed departments
        depts = [
            {"dept_name": "Emergency", "specialty_description": "General Emergency"},
            {"dept_name": "Cardiology", "specialty_description": "Heart related"},
            {"dept_name": "Neurology", "specialty_description": "Brain related"},
            {"dept_name": "General Medicine", "specialty_description": "General"},
            {"dept_name": "Orthopedics", "specialty_description": "Bones"},
            {"dept_name": "Respiratory", "specialty_description": "Lungs"}
        ]
        supabase.table("departments").insert(depts).execute()
        print("✅ 'departments' seeded.")
    else:
        print(f"✅ 'departments' table has {len(res.data)} rows.")
except Exception as e:
    print(f"❌ 'departments' table Error: {e}")
