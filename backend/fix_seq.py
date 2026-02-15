
import os
import time
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("Attempting to fix `patients` sequence sync...")

success = False
attempts = 0
max_attempts = 1000

while not success and attempts < max_attempts:
    try:
        attempts += 1
        # Insert dummy row
        res = supabase.table("patients").insert({
            "full_name": "SEQUENCE_FIX",
            "age": 0,
            "gender": "Fix",
            "contact_info": f"fix_{attempts}"
        }).execute()
        
        # If success, we found a gap or end of sequence
        new_id = res.data[0]['patient_id']
        print(f"✅ Sequence operational at ID: {new_id}")
        
        # Cleanup
        supabase.table("patients").delete().eq("patient_id", new_id).execute()
        success = True
        
    except Exception as e:
        # Expected error: Key already exists
        if "already exists" in str(e):
            print(f"Skipping used ID (attempt {attempts})...")
            continue
        else:
            print(f"❌ Unexpected error: {e}")
            break

if success:
    print("✅ `patients` table sequence fixed.")
else:
    print("❌ Failed to fix `patients` sequence.")
