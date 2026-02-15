
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

DEPARTMENTS = [
    {"dept_name": "Emergency", "specialty_description": "Acute care for critical conditions"},
    {"dept_name": "Cardiology", "specialty_description": "Heart and vascular system disorders"},
    {"dept_name": "Respiratory", "specialty_description": "Lung and respiratory tract diseases"},
    {"dept_name": "Neurology", "specialty_description": "Nervous system disorders"},
    {"dept_name": "General Medicine", "specialty_description": "Adult primary care and internal medicine"},
    {"dept_name": "Orthopedics", "specialty_description": "Musculoskeletal system care"},
]

def init_departments():
    print("initializing departments...")
    
    # Check existing
    existing = supabase.table("departments").select("dept_name").execute()
    existing_names = [d['dept_name'] for d in existing.data]
    print(f"Existing departments: {existing_names}")
    
    to_insert = [d for d in DEPARTMENTS if d['dept_name'] not in existing_names]
    
    if to_insert:
        print(f"Inserting: {to_insert}")
        try:
            supabase.table("departments").insert(to_insert).execute()
            print("Departments initialized successfully.")
        except Exception as e:
            print(f"Error inserting: {e}")
    else:
        print("All departments already exist.")

if __name__ == "__main__":
    init_departments()
