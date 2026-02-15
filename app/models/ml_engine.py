import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from typing import Dict, Any, Tuple
import logging
import os

# FEATURES (EXACT ORDER FROM TRAINING)
FEATURES = [
    'age', 'bp_systolic', 'bp_diastolic', 'heart_rate', 'temperature',
    'chest_pain_severity', 'max_severity', 'symptom_count', 'comorbidities_count',
    'cardiac_history', 'diabetes_status', 'respiratory_history', 'chronic_conditions'
]

class MLEngine:
    def __init__(self, model_dir: str = "app/models"):
        """Load production models + SHAP explainers"""
        self.model_data = self._load_models(model_dir)
        logging.info("✅ MLEngine loaded: Risk & Single-Label Dept Model + SHAP")
    
    def _load_models(self, model_dir: str) -> Dict[str, Any]:
        """Load risk model, dept model, encoders, SHAP explainers"""
        try:
            # Construct absolute paths if needed
            if not os.path.isabs(model_dir):
                 current_dir = os.path.dirname(os.path.abspath(__file__))
                 if os.path.basename(current_dir) == 'models':
                     model_dir = current_dir
                 else:
                     model_dir = os.path.join(current_dir, "../../", model_dir)
            
            # Fallback
            if not os.path.exists(os.path.join(model_dir, "risk_model.joblib")):
                potential_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'risk_model.joblib')
                if os.path.exists(potential_path):
                    model_dir = os.path.dirname(os.path.abspath(__file__))

            logging.info(f"Loading models from: {model_dir}")

            risk_model = joblib.load(os.path.join(model_dir, "risk_model.joblib"))
            dept_model = joblib.load(os.path.join(model_dir, "dept_model.joblib")) # Single model
            risk_encoder = joblib.load(os.path.join(model_dir, "risk_encoder.joblib"))
            dept_encoder = joblib.load(os.path.join(model_dir, "dept_encoder.joblib")) # Single encoder
            
            # SHAP explainer
            risk_explainer = shap.TreeExplainer(risk_model)
            
            return {
                'risk_model': risk_model,
                'dept_model': dept_model,
                'risk_encoder': risk_encoder,
                'dept_encoder': dept_encoder,
                'risk_explainer': risk_explainer,
                'features': FEATURES
            }
        except Exception as e:
            logging.error(f"❌ Model load failed: {e}")
            raise
    
    def preprocess_input(self, patient_data: Dict[str, Any]) -> pd.DataFrame:
        """Convert raw input → model-ready DataFrame"""
        data = {feature: 0 for feature in FEATURES}
        for key, val in patient_data.items():
            if key in data:
                data[key] = val
        return pd.DataFrame([data], columns=FEATURES)
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """FULL PRODUCTION PIPELINE: rule-based overrides + ML predictions"""
        X = self.preprocess_input(patient_data)
        
        # SAFETY OVERRIDES - Catch critical cases before ML
        override = self._check_critical_overrides(patient_data)
        if override:
            logging.info(f"🚨 CRITICAL OVERRIDE: {override['reason']}")
            # Apply smart multi-label rules to override prediction
            prediction = override['prediction']
            prediction = self._apply_smart_multilabel_rules(prediction, patient_data)
            return prediction
        
        # 1. RISK TRIAGE (ML Model)
        risk_pred_idx = self.model_data['risk_model'].predict(X)[0]
        risk_proba = self.model_data['risk_model'].predict_proba(X)[0]
        
        risk_level = self.model_data['risk_encoder'].inverse_transform([risk_pred_idx])[0]
        risk_score = float(np.max(risk_proba))

        # 2. DEPARTMENT SCORES (Single Label Multi-Class)
        dept_pred_idx = self.model_data['dept_model'].predict(X)[0]
        dept_probas = self.model_data['dept_model'].predict_proba(X)[0]
        recommended_dept = self.model_data['dept_encoder'].inverse_transform([dept_pred_idx])[0]

        # Map all department scores
        dept_classes = self.model_data['dept_encoder'].classes_
        dept_scores = {
            str(cls): float(prob) 
            for cls, prob in zip(dept_classes, dept_probas)
        }
        
        # MULTI-LABEL: Get all departments above threshold
        DEPT_THRESHOLD = 0.35  # Conservative threshold
        recommended_depts = [
            dept for dept, score in dept_scores.items() 
            if score >= DEPT_THRESHOLD
        ]
        
        # If no departments above threshold, use the highest scoring one
        if not recommended_depts:
            recommended_depts = [recommended_dept]
        
        # SMART MULTI-LABEL RULES - Add departments based on symptoms/conditions
        # This supplements ML predictions to ensure proper multi-department routing
        
        # Rule 1: Chest pain → Add Cardiology
        if patient_data.get('chest_pain_severity', 0) >= 3:
            if 'Cardiology' not in recommended_depts:
                recommended_depts.append('Cardiology')
                dept_scores['Cardiology'] = max(dept_scores.get('Cardiology', 0), 0.40)
        
        # Rule 2: Head trauma/severe neurological → Add Neurology
        # Check chief_complaint for head/neuro keywords or max_severity >= 4
        chief_complaint = str(patient_data.get('chief_complaint', '')).lower()
        if (patient_data.get('max_severity', 0) >= 4 and 
            any(keyword in chief_complaint for keyword in ['head', 'skull', 'brain', 'seizure', 'stroke', 'neuro', 'consciousness'])):
            if 'Neurology' not in recommended_depts:
                recommended_depts.append('Neurology')
                dept_scores['Neurology'] = max(dept_scores.get('Neurology', 0), 0.45)
        
        # Rule 3: Respiratory symptoms → Add Respiratory
        if patient_data.get('respiratory_history', 0) == 1:
            if 'Respiratory' not in recommended_depts:
                recommended_depts.append('Respiratory')
                dept_scores['Respiratory'] = max(dept_scores.get('Respiratory', 0), 0.40)
        
        # Rule 4: Cardiac history + elevated vitals → Add Cardiology
        if (patient_data.get('cardiac_history', 0) == 1 and 
            (patient_data.get('bp_systolic', 120) >= 160 or patient_data.get('heart_rate', 80) >= 100)):
            if 'Cardiology' not in recommended_depts:
                recommended_depts.append('Cardiology')
                dept_scores['Cardiology'] = max(dept_scores.get('Cardiology', 0), 0.40)
        
        # Rule 5: Trauma/fracture → Add Orthopedics
        if any(keyword in chief_complaint for keyword in ['fracture', 'broken', 'bone', 'joint', 'trauma']):
            if 'Orthopedics' not in recommended_depts and 'Emergency' in recommended_depts:
                recommended_depts.append('Orthopedics')
                dept_scores['Orthopedics'] = max(dept_scores.get('Orthopedics', 0), 0.40)
        
        # Rule 6: Multiple chronic conditions → Add General Medicine
        if patient_data.get('chronic_conditions', 0) >= 2 and len(recommended_depts) == 1:
            if 'General Medicine' not in recommended_depts:
                recommended_depts.append('General Medicine')
                dept_scores['General Medicine'] = max(dept_scores.get('General Medicine', 0), 0.35)
        
        # Primary department is the highest scoring
        primary_dept = max(dept_scores.items(), key=lambda x: x[1])[0]
        
        # 3. EXPLAINABILITY
        explainability = self._real_shap_explanation(X)
        
        # Create prediction dict
        prediction = {
            'risk_level': str(risk_level),
            'risk_score': round(risk_score, 4),
            'recommended_departments': recommended_depts,  # Multi-label array
            'primary_department': str(primary_dept),  # Highest score
            'department_scores': dept_scores,
            'explainability': explainability
        }
        
        # Apply smart multi-label rules
        prediction = self._apply_smart_multilabel_rules(prediction, patient_data)
        return prediction
    
    def _apply_smart_multilabel_rules(self, prediction: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply smart multi-label rules to supplement ML/override predictions"""
        recommended_depts = prediction['recommended_departments']
        dept_scores = prediction['department_scores']
        chief_complaint = str(patient_data.get('chief_complaint', '')).lower()
        
        # Rule 1: Chest pain → Add Cardiology
        if patient_data.get('chest_pain_severity', 0) >= 3:
            if 'Cardiology' not in recommended_depts:
                recommended_depts.append('Cardiology')
                dept_scores['Cardiology'] = max(dept_scores.get('Cardiology', 0), 0.40)
        
        # Rule 2: Head trauma/severe neurological → Add Neurology
        if (patient_data.get('max_severity', 0) >= 4 and 
            any(keyword in chief_complaint for keyword in ['head', 'skull', 'brain', 'seizure', 'stroke', 'neuro', 'consciousness'])):
            if 'Neurology' not in recommended_depts:
                recommended_depts.append('Neurology')
                dept_scores['Neurology'] = max(dept_scores.get('Neurology', 0), 0.45)
        
        # Rule 3: Respiratory symptoms → Add Respiratory
        if patient_data.get('respiratory_history', 0) == 1:
            if 'Respiratory' not in recommended_depts:
                recommended_depts.append('Respiratory')
                dept_scores['Respiratory'] = max(dept_scores.get('Respiratory', 0), 0.40)
        
        # Rule 4: Cardiac history + elevated vitals → Add Cardiology
        if (patient_data.get('cardiac_history', 0) == 1 and 
            (patient_data.get('bp_systolic', 120) >= 160 or patient_data.get('heart_rate', 80) >= 100)):
            if 'Cardiology' not in recommended_depts:
                recommended_depts.append('Cardiology')
                dept_scores['Cardiology'] = max(dept_scores.get('Cardiology', 0), 0.40)
        
        # Rule 5: Trauma/fracture → Add Orthopedics
        if any(keyword in chief_complaint for keyword in ['fracture', 'broken', 'bone', 'joint', 'trauma']):
            if 'Orthopedics' not in recommended_depts and 'Emergency' in recommended_depts:
                recommended_depts.append('Orthopedics')
                dept_scores['Orthopedics'] = max(dept_scores.get('Orthopedics', 0), 0.40)
        
        # Rule 6: Multiple chronic conditions → Add General Medicine
        if patient_data.get('chronic_conditions', 0) >= 2 and len(recommended_depts) == 1:
            if 'General Medicine' not in recommended_depts:
                recommended_depts.append('General Medicine')
                dept_scores['General Medicine'] = max(dept_scores.get('General Medicine', 0), 0.35)
        
        # Update primary department after adding new departments
        prediction['primary_department'] = max(dept_scores.items(), key=lambda x: x[1])[0]
        prediction['recommended_departments'] = recommended_depts
        prediction['department_scores'] = dept_scores
        
        return prediction
    
    def _check_critical_overrides(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based safety checks for critical cases that bypass ML model"""
        
        # Extract key features
        max_sev = data.get('max_severity', 0)
        chest_pain = data.get('chest_pain_severity', 0)
        bp_sys = data.get('bp_systolic', 120)
        bp_dia = data.get('bp_diastolic', 80)
        hr = data.get('heart_rate', 80)
        temp = data.get('temperature', 98.6)
        comorbidities = data.get('comorbidities_count', 0)
        cardiac_hist = data.get('cardiac_history', 0)
        
        # RULE 1: Severe symptoms (max_severity >= 4)
        if max_sev >= 4:
            return {
                'reason': f'Severe symptoms (severity={max_sev})',
                'prediction': {
                    'risk_level': 'High',
                    'risk_score': 0.88,
                    'recommended_departments': ['Emergency'],
                    'primary_department': 'Emergency',
                    'department_scores': {
                        'Emergency': 0.85,
                        'Cardiology': 0.02,
                        'General Medicine': 0.01,
                        'Neurology': 0.01,
                        'Orthopedics': 0.005,
                        'Respiratory': 0.005
                    },
                    'explainability': {
                        'max_severity': max_sev,
                        'chest_pain_severity': chest_pain,
                        'bp_systolic': bp_sys,
                        'comorbidities_count': comorbidities,
                        'cardiac_history': cardiac_hist
                    }
                }
            }
        
        # RULE 2: Severe chest pain (>= 4) with cardiac history
        if chest_pain >= 4 and cardiac_hist == 1:
            return {
                'reason': f'Severe chest pain ({chest_pain}) + cardiac history',
                'prediction': {
                    'risk_level': 'High',
                    'risk_score': 0.90,
                    'recommended_departments': ['Emergency', 'Cardiology'],
                    'primary_department': 'Emergency',
                    'department_scores': {
                        'Emergency': 0.75,
                        'Cardiology': 0.45,
                        'General Medicine': 0.02,
                        'Neurology': 0.01,
                        'Orthopedics': 0.01,
                        'Respiratory': 0.01
                    },
                    'explainability': {
                        'chest_pain_severity': chest_pain,
                        'cardiac_history': cardiac_hist,
                        'bp_systolic': bp_sys,
                        'heart_rate': hr,
                        'age': data.get('age', 40)
                    }
                }
            }
        
        # RULE 3: Critical vitals (BP >= 180/110 OR HR >= 120)
        if bp_sys >= 180 or bp_dia >= 110 or hr >= 120:
            return {
                'reason': f'Critical vitals (BP={bp_sys}/{bp_dia}, HR={hr})',
                'prediction': {
                    'risk_level': 'High',
                    'risk_score': 0.87,
                    'recommended_departments': ['Emergency'],
                    'primary_department': 'Emergency',
                    'department_scores': {
                        'Emergency': 0.80,
                        'Cardiology': 0.10,
                        'General Medicine': 0.02,
                        'Neurology': 0.01,
                        'Orthopedics': 0.01,
                        'Respiratory': 0.01
                    },
                    'explainability': {
                        'bp_systolic': bp_sys,
                        'bp_diastolic': bp_dia,
                        'heart_rate': hr,
                        'age': data.get('age', 40),
                        'cardiac_history': cardiac_hist
                    }
                }
            }
        
        # RULE 4: Multiple comorbidities (>= 3) + elevated vitals
        if comorbidities >= 3 and (bp_sys >= 150 or hr >= 100):
            return {
                'reason': f'Multiple comorbidities ({comorbidities}) + elevated vitals',
                'prediction': {
                    'risk_level': 'High',
                    'risk_score': 0.85,
                    'recommended_departments': ['Emergency'],
                    'primary_department': 'Emergency',
                    'department_scores': {
                        'Emergency': 0.70,
                        'Cardiology': 0.15,
                        'General Medicine': 0.05,
                        'Neurology': 0.02,
                        'Orthopedics': 0.02,
                        'Respiratory': 0.01
                    },
                    'explainability': {
                        'comorbidities_count': comorbidities,
                        'bp_systolic': bp_sys,
                        'heart_rate': hr,
                        'age': data.get('age', 40),
                        'chronic_conditions': data.get('chronic_conditions', 0)
                    }
                }
            }
        
        # No override needed - use ML model
        return None
    
    def _real_shap_explanation(self, X: pd.DataFrame) -> Dict[str, float]:
        """Generate SHAP values for the prediction"""
        try:
            explainer = self.model_data['risk_explainer']
            shap_values = explainer(X)
            
            if hasattr(shap_values, 'values'):
                vals = shap_values.values
            else:
                vals = shap_values
                
            if len(vals.shape) == 3:
                vals = np.abs(vals[0]).sum(axis=1) 
            elif len(vals.shape) == 2:
                vals = np.abs(vals[0])
            else:
                vals = np.abs(vals)

            top_indices = np.argsort(vals)[-5:][::-1]
            
            explainability = {
                FEATURES[i]: float(vals[i]) 
                for i in top_indices
            }
            return {k: round(v, 4) for k, v in explainability.items()}
            
        except Exception as e:
            logging.error(f"❌ SHAP CRASH: {e}")
            return {}

# TEST IT
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        engine = MLEngine(model_dir=current_dir)
        
        test_patient = {
            'visit_id': 3, 'age': 36, 'bp_systolic': 173, 'bp_diastolic': 100,
            'heart_rate': 128, 'temperature': 103.6, 'chest_pain_severity': 5,
            'max_severity': 2, 'symptom_count': 4, 'comorbidities_count': 0,
            'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 0
        }
        
        result = engine.predict(test_patient)
        print("\n🎯 PREDICTION RESULT:")
        import json
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Test failed: {e}")
