
import os
import time
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("Advancing database sequence beyond maximum ID...")

try:
    # 1. Get current Max ID
    res = supabase.table("patients").select("patient_id").order("patient_id", desc=True).limit(1).execute()
    if not res.data:
        print("Table empty, sequence fine.")
        exit(0)
        
    max_id = res.data[0]['patient_id']
    print(f"Current MAX ID: {max_id}")

    attempts = 0
    while True:
        attempts += 1
        try:
            # Insert dummy
            ins_res = supabase.table("patients").insert({
                "full_name": "SEQ_FIX",
                "age": 0,
                "gender": "Fix",
                "contact_info": f"fix_{max_id}_{attempts}"
            }).execute()
            
            new_id = ins_res.data[0]['patient_id']
            print(f"Inserted ID: {new_id}")
            
            # Clean up immediately
            supabase.table("patients").delete().eq("patient_id", new_id).execute()
            
            if new_id > max_id:
                print(f"✅ Sequence advanced successfully! Next ID will be > {max_id}")
                break
                
        except Exception as e:
            if "already exists" in str(e):
                # Only print every 10 attempts to reduce noise
                if attempts % 10 == 0:
                    print(f"Skipping used ID... ({attempts})")
                continue
            else:
                print(f"❌ Unexpected Error: {e}")
                time.sleep(1) # Backoff
                
except Exception as e:
    print(f"❌ Fatal Error: {e}")
