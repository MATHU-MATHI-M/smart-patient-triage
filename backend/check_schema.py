import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

print("Checking 'patients' table columns...")
try:
    # Try fetching 'full_name' specifically
    try:
        supabase.table("patients").select("full_name").limit(1).execute()
        print("✅ 'full_name' YES")
    except Exception as e:
        print(f"❌ 'full_name' NO: {e}")

    # Try fetching 'name' specifically
    try:
        supabase.table("patients").select("name").limit(1).execute()
        print("✅ 'name' YES")
    except Exception as e:
        print(f"❌ 'name' NO: {e}")

except Exception as e:
    print(f"Error: {e}")
