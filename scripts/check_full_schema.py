"""Check all tables in Supabase to find medical history data."""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.core.database import Database
import json

db = Database()
client = db.get_client()

print("="*60)
print("CHECKING SUPABASE SCHEMA")
print("="*60)

# List of tables to check
tables = ['patients', 'patient_visits', 'vitals', 'visit_symptoms', 
          'patient_history', 'medical_history', 'comorbidities']

for table_name in tables:
    try:
        result = client.table(table_name).select('*').limit(1).execute()
        if result.data:
            print(f"\n✅ {table_name.upper()} table exists")
            print(f"   Columns: {list(result.data[0].keys())}")
    except Exception as e:
        print(f"\n❌ {table_name}: {str(e)[:50]}")

# Now fetch a complete visit to see what data is available
print("\n" + "="*60)
print("SAMPLE VISIT DATA (visit_id=1)")
print("="*60)

try:
    visit = client.table('patient_visits').select('*').eq('visit_id', 1).single().execute()
    print("\nVisit data:")
    print(json.dumps(visit.data, indent=2))
except Exception as e:
    print(f"Error: {e}")

try:
    patient_id = visit.data.get('patient_id')
    patient = client.table('patients').select('*').eq('patient_id', patient_id).single().execute()
    print("\nPatient data:")
    print(json.dumps(patient.data, indent=2))
except Exception as e:
    print(f"Error fetching patient: {e}")
