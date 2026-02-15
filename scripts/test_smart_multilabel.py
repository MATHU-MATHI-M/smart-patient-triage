"""
Test smart multi-label rules with specific scenarios.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine

# Test cases that MUST get multiple departments
test_cases = [
    {
        'name': 'Fractured Skull',
        'data': {
            'visit_id': 6001, 'age': 34, 'bp_systolic': 140, 'bp_diastolic': 90,
            'heart_rate': 95, 'temperature': 98.6, 'chest_pain_severity': 0,
            'max_severity': 5, 'symptom_count': 2, 'comorbidities_count': 0,
            'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 0, 'chief_complaint': 'fractured skull, loss of consciousness'
        },
        'expected': 'Emergency + Neurology + Orthopedics'
    },
    {
        'name': 'Severe Chest Pain + Cardiac History',
        'data': {
            'visit_id': 6002, 'age': 65, 'bp_systolic': 180, 'bp_diastolic': 110,
            'heart_rate': 120, 'temperature': 99.5, 'chest_pain_severity': 5,
            'max_severity': 5, 'symptom_count': 3, 'comorbidities_count': 2,
            'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0,
            'chronic_conditions': 2, 'chief_complaint': 'severe chest pain'
        },
        'expected': 'Emergency + Cardiology'
    },
    {
        'name': 'Respiratory Distress + Cardiac Issues',
        'data': {
            'visit_id': 6003, 'age': 62, 'bp_systolic': 165, 'bp_diastolic': 98,
            'heart_rate': 105, 'temperature': 99.8, 'chest_pain_severity': 2,
            'max_severity': 4, 'symptom_count': 3, 'comorbidities_count': 2,
            'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1,
            'chronic_conditions': 2, 'chief_complaint': 'shortness of breath'
        },
        'expected': 'Emergency + Respiratory + Cardiology'
    },
    {
        'name': 'Head Trauma + Stroke Symptoms',
        'data': {
            'visit_id': 6004, 'age': 58, 'bp_systolic': 175, 'bp_diastolic': 105,
            'heart_rate': 95, 'temperature': 99.0, 'chest_pain_severity': 0,
            'max_severity': 5, 'symptom_count': 2, 'comorbidities_count': 1,
            'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 1, 'chief_complaint': 'head injury, possible stroke'
        },
        'expected': 'Emergency + Neurology'
    }
]

print("="*100)
print("SMART MULTI-LABEL RULES TEST")
print("="*100)

engine = MLEngine(model_dir='app/models')

all_passed = True
for case in test_cases:
    print(f"\n{'='*100}")
    print(f"TEST: {case['name']}")
    print(f"Expected: {case['expected']}")
    print(f"{'='*100}")
    
    prediction = engine.predict(case['data'])
    
    print(f"\n✅ RESULT:")
    print(f"   Risk: {prediction['risk_level']} ({prediction['risk_score']:.2f})")
    print(f"   Recommended Departments: {prediction['recommended_departments']}")
    print(f"   Primary Department: {prediction['primary_department']}")
    
    print(f"\n   Department Scores:")
    for dept in prediction['recommended_departments']:
        score = prediction['department_scores'][dept]
        print(f"      ✓ {dept}: {score:.3f}")
    
    # Check if got multiple departments
    num_depts = len(prediction['recommended_departments'])
    if num_depts > 1:
        print(f"\n   ✅ PASS - Got {num_depts} departments (multi-label working!)")
    else:
        print(f"\n   ❌ FAIL - Only got 1 department")
        all_passed = False

print("\n" + "="*100)
if all_passed:
    print("✅ ALL TESTS PASSED - Smart multi-label rules working correctly!")
else:
    print("❌ SOME TESTS FAILED - Review the rules")
print("="*100)
