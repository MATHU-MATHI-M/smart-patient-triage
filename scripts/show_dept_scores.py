"""
Simple analysis showing department scores for patients that should get multiple departments.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine

# Patients that SHOULD get multiple departments
patients = [
    {'name': 'Severe Cardiac Emergency', 'age': 65, 'bp_systolic': 180, 'bp_diastolic': 110, 'heart_rate': 120, 'temperature': 99.5, 'chest_pain_severity': 5, 'max_severity': 5, 'symptom_count': 3, 'comorbidities_count': 2, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0, 'chronic_conditions': 2, 'visit_id': 5001},
    {'name': 'Multi-Comorbid + Resp', 'age': 70, 'bp_systolic': 165, 'bp_diastolic': 98, 'heart_rate': 105, 'temperature': 99.8, 'chest_pain_severity': 2, 'max_severity': 4, 'symptom_count': 3, 'comorbidities_count': 3, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1, 'chronic_conditions': 3, 'visit_id': 5002},
    {'name': 'Moderate Cardiac', 'age': 55, 'bp_systolic': 150, 'bp_diastolic': 95, 'heart_rate': 95, 'temperature': 99.0, 'chest_pain_severity': 3, 'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 1, 'visit_id': 5003},
]

engine = MLEngine(model_dir='app/models')

print("\n" + "="*80)
print("DEPARTMENT SCORES ANALYSIS")
print("="*80)

for p in patients:
    pred = engine.predict(p)
    print(f"\n{p['name']} (Age {p['age']}, ChestPain={p['chest_pain_severity']}, MaxSev={p['max_severity']})")
    print(f"  Risk: {pred['risk_level']} ({pred['risk_score']:.2f})")
    print(f"  Recommended: {pred['recommended_departments']}")
    print(f"  Scores:")
    for dept, score in sorted(pred['department_scores'].items(), key=lambda x: x[1], reverse=True):
        mark = "✓" if score >= 0.35 else " "
        print(f"    {mark} {dept:<20} {score:.3f}")

print("\n" + "="*80)
print("THRESHOLD: 0.35 (departments >= 0.35 are recommended)")
print("="*80)
