from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            cls._client = create_client(settings.supabase_url, settings.supabase_key)
            logger.info("Supabase client initialized")
        return cls._client
    
    @classmethod
    def get_visit_features(cls, visit_id: int) -> dict:
        """Fetch complete visit data for rule-based triage engine"""
        client = cls.get_client()
        
        # Get visit basics
        response = client.table('patient_visits').select('visit_id, chief_complaint, patient_id').eq('visit_id', visit_id).single().execute()
        visit = response.data
        
        if not visit:
            raise ValueError(f"Visit {visit_id} not found")
        
        # Patient info
        patient_response = client.table('patients').select('age, gender').eq('patient_id', visit['patient_id']).single().execute()
        patient = patient_response.data or {}
        
        # Vitals
        vitals_response = client.table('vitals').select('bp_systolic, bp_diastolic, heart_rate, temperature').eq('visit_id', visit_id).execute()
        vitals_data = vitals_response.data[0] if vitals_response.data else {}
        
        # Symptoms (full array)
        symptoms_response = client.table('visit_symptoms').select('symptom_name, severity_score, duration').eq('visit_id', visit_id).execute()
        symptoms = symptoms_response.data or []
        
        # Medical History (full array)
        patient_id = visit['patient_id']
        history_response = client.table('patient_medical_history').select('condition_name, is_chronic, diagnosis_date').eq('patient_id', patient_id).execute()
        medical_history = history_response.data or []
        
        # Return structured data for rule engine
        return {
            'visit_id': visit_id,
            'age': patient.get('age', 40),
            'gender': patient.get('gender', 'M'),
            'chief_complaint': visit.get('chief_complaint', 'general'),
            'vitals': {
                'bp_systolic': vitals_data.get('bp_systolic', 120),
                'bp_diastolic': vitals_data.get('bp_diastolic', 80),
                'heart_rate': vitals_data.get('heart_rate', 80),
                'temperature': float(vitals_data.get('temperature', 98.6))
            },
            'symptoms': symptoms,
            'medical_history': medical_history
        }

    @classmethod
    def save_prediction(cls, visit_id: int, prediction: dict) -> dict:
        """Save triage prediction to Supabase."""
        client = cls.get_client()
        
        data = {
            'visit_id': visit_id,
            'risk_level': prediction['risk_level'],
            'risk_score': prediction['risk_score'],
            'recommended_department': prediction.get('primary_department', prediction.get('recommended_department')),
            'department_scores': prediction['department_scores'],
            'explainability': prediction['explainability']
        }
        
        try:
            response = client.table('triage_predictions').insert(data).execute()
            if response.data:
                logger.info(f"✅ Saved prediction for visit {visit_id}")
                return response.data[0]
            else:
                logger.warning(f"⚠️ Failed to save prediction for visit {visit_id}")
                return {}
        except Exception as e:
            logger.error(f"❌ DB Insert Error: {e}")
            return {}

