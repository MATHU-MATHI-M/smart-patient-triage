"""
Show detailed JSON output for sample patients to analyze department scores.
"""
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine

# Test cases that SHOULD get multiple departments
test_cases = [
    {
        'name': 'Severe Chest Pain + Cardiac History + High BP',
        'data': {
            'visit_id': 4001, 'age': 65, 'bp_systolic': 180, 'bp_diastolic': 110,
            'heart_rate': 120, 'temperature': 99.5, 'chest_pain_severity': 5,
            'max_severity': 5, 'symptom_count': 3, 'comorbidities_count': 2,
            'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0,
            'chronic_conditions': 2
        }
    },
    {
        'name': 'Multiple Comorbidities + Respiratory + Cardiac',
        'data': {
            'visit_id': 4002, 'age': 70, 'bp_systolic': 165, 'bp_diastolic': 98,
            'heart_rate': 105, 'temperature': 99.8, 'chest_pain_severity': 2,
            'max_severity': 4, 'symptom_count': 3, 'comorbidities_count': 3,
            'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1,
            'chronic_conditions': 3
        }
    },
    {
        'name': 'Moderate Chest Pain + Cardiac History',
        'data': {
            'visit_id': 4003, 'age': 55, 'bp_systolic': 150, 'bp_diastolic': 95,
            'heart_rate': 95, 'temperature': 99.0, 'chest_pain_severity': 3,
            'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1,
            'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 1
        }
    },
    {
        'name': 'Respiratory Distress + Cardiac Issues',
        'data': {
            'visit_id': 4004, 'age': 62, 'bp_systolic': 155, 'bp_diastolic': 92,
            'heart_rate': 100, 'temperature': 99.5, 'chest_pain_severity': 2,
            'max_severity': 4, 'symptom_count': 3, 'comorbidities_count': 2,
            'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 1,
            'chronic_conditions': 2
        }
    }
]

print("="*100)
print("DETAILED DEPARTMENT SCORES ANALYSIS")
print("="*100)

engine = MLEngine(model_dir='app/models')

for i, case in enumerate(test_cases, 1):
    print(f"\n{'='*100}")
    print(f"PATIENT {i}: {case['name']}")
    print(f"{'='*100}")
    
    prediction = engine.predict(case['data'])
    
    print(f"\n📊 PREDICTION SUMMARY:")
    print(f"   Risk Level: {prediction['risk_level']}")
    print(f"   Risk Score: {prediction['risk_score']:.4f}")
    print(f"   Recommended Departments: {prediction['recommended_departments']}")
    print(f"   Primary Department: {prediction['primary_department']}")
    
    print(f"\n📈 ALL DEPARTMENT SCORES (sorted by score):")
    sorted_depts = sorted(prediction['department_scores'].items(), key=lambda x: x[1], reverse=True)
    for dept, score in sorted_depts:
        threshold_marker = "✓ RECOMMENDED" if score >= 0.35 else "  (below threshold)"
        print(f"   {dept:<25} {score:.4f}  {threshold_marker}")
    
    print(f"\n🔍 EXPLAINABILITY (Top 5 features):")
    for feature, value in prediction['explainability'].items():
        print(f"   {feature:<30} {value}")
    
    print(f"\n📋 FULL JSON OUTPUT:")
    print(json.dumps(prediction, indent=2))

print("\n" + "="*100)
print("THRESHOLD ANALYSIS")
print("="*100)
print("Current threshold: 0.35")
print("\nIf you see departments with scores like 0.25-0.34 that should be recommended,")
print("we can lower the threshold to 0.25 or 0.30 to include more departments.")
print("="*100)
