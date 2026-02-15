
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def clear_queue_data():
    """
    Clears all data from the department_queue and related tables to reset the system.
    This maintains the schema but removes the transactional data.
    """
    print("Clearing data...")
    
    # Delete from child tables first to respect foreign key constraints
    # Order matters: queue -> predictions -> symptoms/vitals -> visits -> history -> patients
    
    try:
        print("Trimming department_queue...")
        supabase.table("department_queue").delete().neq("queue_id", 0).execute()
        
        print("Trimming triage_predictions...")
        supabase.table("triage_predictions").delete().neq("prediction_id", 0).execute()
        
        print("Trimming visit_symptoms...")
        supabase.table("visit_symptoms").delete().neq("symptom_id", 0).execute()
        
        print("Trimming vitals...")
        supabase.table("vitals").delete().neq("vitals_id", 0).execute()
        
        print("Trimming patient_visits...")
        supabase.table("patient_visits").delete().neq("visit_id", 0).execute()
        
        print("Trimming patient_medical_history...")
        supabase.table("patient_medical_history").delete().neq("history_id", 0).execute()
        
        print("Trimming patients...")
        supabase.table("patients").delete().neq("patient_id", 0).execute()
        
        print("SUCCESS: All transactional data cleared.")
        
    except Exception as e:
        print(f"ERROR: Failed to clear data. {e}")

if __name__ == "__main__":
    clear_queue_data()
