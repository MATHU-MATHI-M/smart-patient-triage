"""
Test multi-label department recommendations.
"""
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine

# Test cases for multi-label
test_cases = [
    {
        'name': 'Single Department (Low Risk)',
        'data': {
            'visit_id': 3001, 'age': 25, 'bp_systolic': 120, 'bp_diastolic': 80,
            'heart_rate': 72, 'temperature': 98.6, 'chest_pain_severity': 0,
            'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0,
            'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 0
        },
        'expected': 'Should recommend 1 department (General Medicine or similar)'
    },
    {
        'name': 'Multi-Department (Severe Chest Pain + Cardiac History)',
        'data': {
            'visit_id': 3002, 'age': 65, 'bp_systolic': 150, 'bp_diastolic': 95,
            'heart_rate': 100, 'temperature': 99.0, 'chest_pain_severity': 5,
            'max_severity': 4, 'symptom_count': 2, 'comorbidities_count': 1,
            'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 1
        },
        'expected': 'Should recommend Emergency + Cardiology'
    },
    {
        'name': 'Single Department (Severe Trauma)',
        'data': {
            'visit_id': 3003, 'age': 34, 'bp_systolic': 140, 'bp_diastolic': 90,
            'heart_rate': 95, 'temperature': 98.6, 'chest_pain_severity': 0,
            'max_severity': 5, 'symptom_count': 2, 'comorbidities_count': 0,
            'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 0
        },
        'expected': 'Should recommend Emergency only'
    }
]

print("="*80)
print("MULTI-LABEL DEPARTMENT RECOMMENDATION TEST")
print("="*80)

engine = MLEngine(model_dir='app/models')

for case in test_cases:
    print(f"\n📋 {case['name']}")
    print(f"   Expected: {case['expected']}")
    
    prediction = engine.predict(case['data'])
    
    print(f"\n   ✅ Results:")
    print(f"      Risk: {prediction['risk_level']} ({prediction['risk_score']:.2f})")
    print(f"      Recommended Departments: {prediction['recommended_departments']}")
    print(f"      Primary Department: {prediction['primary_department']}")
    print(f"\n      Department Scores:")
    for dept, score in sorted(prediction['department_scores'].items(), key=lambda x: x[1], reverse=True)[:3]:
        marker = "✓" if score >= 0.35 else " "
        print(f"        {marker} {dept}: {score:.3f}")
    print(f"\n      Top Explainability:")
    for feature, value in list(prediction['explainability'].items())[:3]:
        print(f"        - {feature}: {value}")
    print("-"*80)

print("\n" + "="*80)
print("✅ Multi-label implementation complete!")
print("="*80)
