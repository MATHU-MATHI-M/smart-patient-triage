"""
Generate 20 diverse dummy patients and test ML predictions.
NO database insertion - just testing the model locally.
"""
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine

# 20 diverse test cases
test_patients = [
    # 1. CRITICAL - Severe chest pain, high BP, cardiac history
    {
        'visit_id': 1001, 'age': 65, 'bp_systolic': 180, 'bp_diastolic': 110,
        'heart_rate': 120, 'temperature': 99.5, 'chest_pain_severity': 5,
        'max_severity': 5, 'symptom_count': 3, 'comorbidities_count': 2,
        'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0,
        'chronic_conditions': 2
    },
    # 2. CRITICAL - Fractured skull, loss of consciousness
    {
        'visit_id': 1002, 'age': 34, 'bp_systolic': 140, 'bp_diastolic': 90,
        'heart_rate': 95, 'temperature': 98.6, 'chest_pain_severity': 0,
        'max_severity': 5, 'symptom_count': 2, 'comorbidities_count': 0,
        'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
        'chronic_conditions': 0
    },
    # 3. HIGH - Severe headache, high BP
    {
        'visit_id': 1003, 'age': 55, 'bp_systolic': 170, 'bp_diastolic': 100,
        'heart_rate': 88, 'temperature': 98.8, 'chest_pain_severity': 0,
        'max_severity': 4, 'symptom_count': 2, 'comorbidities_count': 1,
        'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0,
        'chronic_conditions': 1
    },
    # 4. MEDIUM - Moderate chest pain, normal vitals
    {
        'visit_id': 1004, 'age': 45, 'bp_systolic': 130, 'bp_diastolic': 85,
        'heart_rate': 78, 'temperature': 98.6, 'chest_pain_severity': 3,
        'max_severity': 3, 'symptom_count': 1, 'comorbidities_count': 0,
        'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
        'chronic_conditions': 0
    },
    # 5. LOW - Healthy young adult, minor complaint
    {
        'visit_id': 1005, 'age': 25, 'bp_systolic': 120, 'bp_diastolic': 80,
        'heart_rate': 72, 'temperature': 98.6, 'chest_pain_severity': 0,
        'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0,
        'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
        'chronic_conditions': 0
    },
    # 6. HIGH - Respiratory distress, asthma history
    {
        'visit_id': 1006, 'age': 42, 'bp_systolic': 135, 'bp_diastolic': 88,
        'heart_rate': 105, 'temperature': 99.2, 'chest_pain_severity': 0,
        'max_severity': 4, 'symptom_count': 2, 'comorbidities_count': 1,
        'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 1,
        'chronic_conditions': 1
    },
    # 7. MEDIUM - Diabetic with moderate symptoms
    {
        'visit_id': 1007, 'age': 58, 'bp_systolic': 145, 'bp_diastolic': 92,
        'heart_rate': 82, 'temperature': 99.0, 'chest_pain_severity': 0,
        'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1,
        'cardiac_history': 0, 'diabetes_status': 2, 'respiratory_history': 0,
        'chronic_conditions': 1
    },
    # 8. LOW - Elderly but stable
    {
        'visit_id': 1008, 'age': 78, 'bp_systolic': 128, 'bp_diastolic': 82,
        'heart_rate': 75, 'temperature': 98.4, 'chest_pain_severity': 0,
        'max_severity': 2, 'symptom_count': 1, 'comorbidities_count': 2,
        'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0,
        'chronic_conditions': 2
    },
    # 9. CRITICAL - Multiple severe symptoms, multiple comorbidities
    {
        'visit_id': 1009, 'age': 70, 'bp_systolic': 190, 'bp_diastolic': 115,
        'heart_rate': 130, 'temperature': 100.5, 'chest_pain_severity': 4,
        'max_severity': 5, 'symptom_count': 4, 'comorbidities_count': 3,
        'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1,
        'chronic_conditions': 3
    },
    # 10. LOW - Young, healthy, minor issue
    {
        'visit_id': 1010, 'age': 22, 'bp_systolic': 118, 'bp_diastolic': 78,
        'heart_rate': 70, 'temperature': 98.5, 'chest_pain_severity': 0,
        'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0,
        'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0,
        'chronic_conditions': 0
    },
    # 11-20: More diverse cases
    {'visit_id': 1011, 'age': 50, 'bp_systolic': 155, 'bp_diastolic': 95, 'heart_rate': 90, 'temperature': 99.0, 'chest_pain_severity': 2, 'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 1},
    {'visit_id': 1012, 'age': 30, 'bp_systolic': 125, 'bp_diastolic': 82, 'heart_rate': 76, 'temperature': 98.7, 'chest_pain_severity': 0, 'max_severity': 2, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'visit_id': 1013, 'age': 62, 'bp_systolic': 165, 'bp_diastolic': 98, 'heart_rate': 95, 'temperature': 99.5, 'chest_pain_severity': 3, 'max_severity': 4, 'symptom_count': 3, 'comorbidities_count': 2, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0, 'chronic_conditions': 2},
    {'visit_id': 1014, 'age': 28, 'bp_systolic': 122, 'bp_diastolic': 80, 'heart_rate': 74, 'temperature': 98.6, 'chest_pain_severity': 0, 'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'visit_id': 1015, 'age': 48, 'bp_systolic': 148, 'bp_diastolic': 92, 'heart_rate': 85, 'temperature': 99.2, 'chest_pain_severity': 1, 'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 0, 'diabetes_status': 2, 'respiratory_history': 0, 'chronic_conditions': 1},
    {'visit_id': 1016, 'age': 75, 'bp_systolic': 175, 'bp_diastolic': 105, 'heart_rate': 110, 'temperature': 100.0, 'chest_pain_severity': 4, 'max_severity': 5, 'symptom_count': 3, 'comorbidities_count': 3, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1, 'chronic_conditions': 3},
    {'visit_id': 1017, 'age': 35, 'bp_systolic': 128, 'bp_diastolic': 84, 'heart_rate': 78, 'temperature': 98.8, 'chest_pain_severity': 0, 'max_severity': 2, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'visit_id': 1018, 'age': 52, 'bp_systolic': 160, 'bp_diastolic': 96, 'heart_rate': 92, 'temperature': 99.3, 'chest_pain_severity': 2, 'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 1},
    {'visit_id': 1019, 'age': 26, 'bp_systolic': 120, 'bp_diastolic': 78, 'heart_rate': 72, 'temperature': 98.5, 'chest_pain_severity': 0, 'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'visit_id': 1020, 'age': 68, 'bp_systolic': 185, 'bp_diastolic': 112, 'heart_rate': 125, 'temperature': 100.2, 'chest_pain_severity': 5, 'max_severity': 5, 'symptom_count': 4, 'comorbidities_count': 3, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1, 'chronic_conditions': 3},
]

print("="*80)
print("TESTING ML MODEL WITH 20 DIVERSE PATIENTS")
print("="*80)

engine = MLEngine(model_dir='app/models')

results = []
for patient in test_patients:
    prediction = engine.predict(patient)
    results.append({
        'visit_id': patient['visit_id'],
        'age': patient['age'],
        'max_severity': patient['max_severity'],
        'chest_pain': patient['chest_pain_severity'],
        'comorbidities': patient['comorbidities_count'],
        'risk_level': prediction['risk_level'],
        'risk_score': prediction['risk_score'],
        'department': prediction['recommended_department']
    })

# Display results in a table
print(f"\n{'ID':<6} {'Age':<5} {'MaxSev':<7} {'ChestP':<7} {'Comor':<6} {'Risk':<8} {'Score':<6} {'Department':<20}")
print("-"*80)
for r in results:
    print(f"{r['visit_id']:<6} {r['age']:<5} {r['max_severity']:<7} {r['chest_pain']:<7} {r['comorbidities']:<6} {r['risk_level']:<8} {r['risk_score']:.2f}   {r['department']:<20}")

# Summary statistics
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
risk_counts = {}
dept_counts = {}
for r in results:
    risk_counts[r['risk_level']] = risk_counts.get(r['risk_level'], 0) + 1
    dept_counts[r['department']] = dept_counts.get(r['department'], 0) + 1

print("\nRisk Level Distribution:")
for risk, count in sorted(risk_counts.items()):
    print(f"  {risk}: {count}")

print("\nDepartment Distribution:")
for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {dept}: {count}")

print("\n" + "="*80)
print("CRITICAL CASES TO VERIFY:")
print("="*80)
print("Patient 1001 (Severe chest pain, cardiac history) -> Should be High/Emergency")
print("Patient 1002 (Fractured skull, max severity 5) -> Should be High/Emergency")
print("Patient 1009 (Multiple severe, 3 comorbidities) -> Should be High/Emergency")
print("Patient 1020 (Chest pain 5, BP 185/112) -> Should be High/Emergency")
