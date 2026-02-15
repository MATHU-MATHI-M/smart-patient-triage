"""
Generate JSON outputs and save to file.
"""
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine

scenarios = [
    {
        'name': 'Fractured Skull',
        'data': {
            'visit_id': 8001, 'age': 34, 'bp_systolic': 140, 'bp_diastolic': 90,
            'heart_rate': 95, 'temperature': 98.6, 'chest_pain_severity': 0,
            'max_severity': 5, 'symptom_count': 2, 'comorbidities_count': 0,
            'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 0, 'chief_complaint': 'fractured skull, loss of consciousness'
        }
    },
    {
        'name': 'Severe Chest Pain + Cardiac History',
        'data': {
            'visit_id': 8002, 'age': 65, 'bp_systolic': 180, 'bp_diastolic': 110,
            'heart_rate': 120, 'temperature': 99.5, 'chest_pain_severity': 5,
            'max_severity': 5, 'symptom_count': 3, 'comorbidities_count': 2,
            'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0,
            'chronic_conditions': 2, 'chief_complaint': 'severe chest pain'
        }
    },
    {
        'name': 'Respiratory Distress + Cardiac',
        'data': {
            'visit_id': 8003, 'age': 62, 'bp_systolic': 165, 'bp_diastolic': 98,
            'heart_rate': 105, 'temperature': 99.8, 'chest_pain_severity': 2,
            'max_severity': 4, 'symptom_count': 3, 'comorbidities_count': 2,
            'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1,
            'chronic_conditions': 2, 'chief_complaint': 'shortness of breath'
        }
    },
    {
        'name': 'Low Risk - Minor Headache',
        'data': {
            'visit_id': 8004, 'age': 25, 'bp_systolic': 120, 'bp_diastolic': 80,
            'heart_rate': 72, 'temperature': 98.6, 'chest_pain_severity': 0,
            'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0,
            'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 0, 'chief_complaint': 'mild headache'
        }
    }
]

engine = MLEngine(model_dir='app/models')

results = {}
for scenario in scenarios:
    prediction = engine.predict(scenario['data'])
    results[scenario['name']] = prediction
    
    print(f"\n{'='*80}")
    print(f"{scenario['name']}")
    print(f"{'='*80}")
    print(json.dumps(prediction, indent=2))

# Save to file
with open('model_outputs.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*80}")
print("✅ Saved to model_outputs.json")
print(f"{'='*80}")
