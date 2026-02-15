"""Check what medical history tables/columns exist in Supabase."""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.core.database import Database

db = Database()
client = db.get_client()

print("Checking Supabase schema...")
print("="*60)

# Check patients table
try:
    patient = client.table('patients').select('*').limit(1).execute()
    if patient.data:
        print("\nPATIENTS table columns:")
        print(list(patient.data[0].keys()))
except Exception as e:
    print(f"Error fetching patients: {e}")

# Check if there's a medical_history or patient_history table
try:
    history = client.table('patient_history').select('*').limit(1).execute()
    if history.data:
        print("\nPATIENT_HISTORY table columns:")
        print(list(history.data[0].keys()))
except Exception as e:
    print(f"\nNo patient_history table: {e}")

# Check patient_visits
try:
    visit = client.table('patient_visits').select('*').limit(1).execute()
    if visit.data:
        print("\nPATIENT_VISITS table columns:")
        print(list(visit.data[0].keys()))
except Exception as e:
    print(f"Error fetching visits: {e}")
