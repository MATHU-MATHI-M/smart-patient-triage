"""
Comprehensive test showing rule-based overrides working correctly.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine

# Critical test cases that MUST be High Risk + Emergency
critical_cases = [
    {
        'name': 'Fractured Skull (max_severity=5)',
        'data': {
            'visit_id': 2001, 'age': 34, 'bp_systolic': 140, 'bp_diastolic': 90,
            'heart_rate': 95, 'temperature': 98.6, 'chest_pain_severity': 0,
            'max_severity': 5, 'symptom_count': 2, 'comorbidities_count': 0,
            'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 0
        }
    },
    {
        'name': 'Severe Chest Pain + Cardiac History',
        'data': {
            'visit_id': 2002, 'age': 65, 'bp_systolic': 150, 'bp_diastolic': 95,
            'heart_rate': 100, 'temperature': 99.0, 'chest_pain_severity': 5,
            'max_severity': 4, 'symptom_count': 2, 'comorbidities_count': 1,
            'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 1
        }
    },
    {
        'name': 'Critical BP (185/112)',
        'data': {
            'visit_id': 2003, 'age': 68, 'bp_systolic': 185, 'bp_diastolic': 112,
            'heart_rate': 90, 'temperature': 98.8, 'chest_pain_severity': 2,
            'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 2,
            'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0,
            'chronic_conditions': 2
        }
    },
    {
        'name': 'Critical Heart Rate (125 bpm)',
        'data': {
            'visit_id': 2004, 'age': 55, 'bp_systolic': 160, 'bp_diastolic': 100,
            'heart_rate': 125, 'temperature': 99.5, 'chest_pain_severity': 3,
            'max_severity': 3, 'symptom_count': 3, 'comorbidities_count': 1,
            'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0,
            'chronic_conditions': 1
        }
    },
    {
        'name': 'Multiple Comorbidities (3) + Elevated Vitals',
        'data': {
            'visit_id': 2005, 'age': 70, 'bp_systolic': 165, 'bp_diastolic': 98,
            'heart_rate': 105, 'temperature': 99.8, 'chest_pain_severity': 2,
            'max_severity': 3, 'symptom_count': 3, 'comorbidities_count': 3,
            'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1,
            'chronic_conditions': 3
        }
    }
]

print("="*80)
print("RULE-BASED SAFETY OVERRIDE VERIFICATION")
print("="*80)
print("\nTesting critical cases that MUST be routed to Emergency...\n")

engine = MLEngine(model_dir='app/models')

all_passed = True
for case in critical_cases:
    prediction = engine.predict(case['data'])
    
    risk = prediction['risk_level']
    dept = prediction['recommended_department']
    score = prediction['risk_score']
    
    # Check if correctly classified
    is_high_risk = risk == 'High'
    is_emergency = dept == 'Emergency'
    passed = is_high_risk and is_emergency
    
    status = "✅ PASS" if passed else "❌ FAIL"
    all_passed = all_passed and passed
    
    print(f"{status} | {case['name']}")
    print(f"       Risk: {risk} ({score:.2f}) | Department: {dept}")
    if not passed:
        print(f"       ⚠️  EXPECTED: High Risk + Emergency")
    print()

print("="*80)
if all_passed:
    print("✅ ALL CRITICAL CASES PASSED - Rule-based overrides working correctly!")
else:
    print("❌ SOME CASES FAILED - Review the rules")
print("="*80)
