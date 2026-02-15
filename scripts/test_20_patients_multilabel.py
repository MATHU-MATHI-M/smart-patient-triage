"""
Enhanced 20-patient test showing multi-label department recommendations.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine

# 20 diverse test cases
test_patients = [
    # CRITICAL CASES
    {'id': 1, 'age': 65, 'bp_systolic': 180, 'bp_diastolic': 110, 'heart_rate': 120, 'temperature': 99.5, 'chest_pain_severity': 5, 'max_severity': 5, 'symptom_count': 3, 'comorbidities_count': 2, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0, 'chronic_conditions': 2},
    {'id': 2, 'age': 34, 'bp_systolic': 140, 'bp_diastolic': 90, 'heart_rate': 95, 'temperature': 98.6, 'chest_pain_severity': 0, 'max_severity': 5, 'symptom_count': 2, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'id': 3, 'age': 70, 'bp_systolic': 190, 'bp_diastolic': 115, 'heart_rate': 130, 'temperature': 100.5, 'chest_pain_severity': 4, 'max_severity': 5, 'symptom_count': 4, 'comorbidities_count': 3, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1, 'chronic_conditions': 3},
    
    # HIGH RISK
    {'id': 4, 'age': 55, 'bp_systolic': 170, 'bp_diastolic': 100, 'heart_rate': 88, 'temperature': 98.8, 'chest_pain_severity': 0, 'max_severity': 4, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 1},
    {'id': 5, 'age': 42, 'bp_systolic': 135, 'bp_diastolic': 88, 'heart_rate': 105, 'temperature': 99.2, 'chest_pain_severity': 0, 'max_severity': 4, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 1, 'chronic_conditions': 1},
    
    # MEDIUM RISK
    {'id': 6, 'age': 45, 'bp_systolic': 130, 'bp_diastolic': 85, 'heart_rate': 78, 'temperature': 98.6, 'chest_pain_severity': 3, 'max_severity': 3, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'id': 7, 'age': 58, 'bp_systolic': 145, 'bp_diastolic': 92, 'heart_rate': 82, 'temperature': 99.0, 'chest_pain_severity': 0, 'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 0, 'diabetes_status': 2, 'respiratory_history': 0, 'chronic_conditions': 1},
    {'id': 8, 'age': 50, 'bp_systolic': 155, 'bp_diastolic': 95, 'heart_rate': 90, 'temperature': 99.0, 'chest_pain_severity': 2, 'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 1},
    
    # LOW RISK
    {'id': 9, 'age': 25, 'bp_systolic': 120, 'bp_diastolic': 80, 'heart_rate': 72, 'temperature': 98.6, 'chest_pain_severity': 0, 'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'id': 10, 'age': 22, 'bp_systolic': 118, 'bp_diastolic': 78, 'heart_rate': 70, 'temperature': 98.5, 'chest_pain_severity': 0, 'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'id': 11, 'age': 30, 'bp_systolic': 125, 'bp_diastolic': 82, 'heart_rate': 76, 'temperature': 98.7, 'chest_pain_severity': 0, 'max_severity': 2, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'id': 12, 'age': 28, 'bp_systolic': 122, 'bp_diastolic': 80, 'heart_rate': 74, 'temperature': 98.6, 'chest_pain_severity': 0, 'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    
    # MIXED
    {'id': 13, 'age': 62, 'bp_systolic': 165, 'bp_diastolic': 98, 'heart_rate': 95, 'temperature': 99.5, 'chest_pain_severity': 3, 'max_severity': 4, 'symptom_count': 3, 'comorbidities_count': 2, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 0, 'chronic_conditions': 2},
    {'id': 14, 'age': 48, 'bp_systolic': 148, 'bp_diastolic': 92, 'heart_rate': 85, 'temperature': 99.2, 'chest_pain_severity': 1, 'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 0, 'diabetes_status': 2, 'respiratory_history': 0, 'chronic_conditions': 1},
    {'id': 15, 'age': 75, 'bp_systolic': 175, 'bp_diastolic': 105, 'heart_rate': 110, 'temperature': 100.0, 'chest_pain_severity': 4, 'max_severity': 5, 'symptom_count': 3, 'comorbidities_count': 3, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1, 'chronic_conditions': 3},
    {'id': 16, 'age': 35, 'bp_systolic': 128, 'bp_diastolic': 84, 'heart_rate': 78, 'temperature': 98.8, 'chest_pain_severity': 0, 'max_severity': 2, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'id': 17, 'age': 52, 'bp_systolic': 160, 'bp_diastolic': 96, 'heart_rate': 92, 'temperature': 99.3, 'chest_pain_severity': 2, 'max_severity': 3, 'symptom_count': 2, 'comorbidities_count': 1, 'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 1},
    {'id': 18, 'age': 26, 'bp_systolic': 120, 'bp_diastolic': 78, 'heart_rate': 72, 'temperature': 98.5, 'chest_pain_severity': 0, 'max_severity': 1, 'symptom_count': 1, 'comorbidities_count': 0, 'cardiac_history': 0, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 0},
    {'id': 19, 'age': 68, 'bp_systolic': 185, 'bp_diastolic': 112, 'heart_rate': 125, 'temperature': 100.2, 'chest_pain_severity': 5, 'max_severity': 5, 'symptom_count': 4, 'comorbidities_count': 3, 'cardiac_history': 1, 'diabetes_status': 2, 'respiratory_history': 1, 'chronic_conditions': 3},
    {'id': 20, 'age': 78, 'bp_systolic': 128, 'bp_diastolic': 82, 'heart_rate': 75, 'temperature': 98.4, 'chest_pain_severity': 0, 'max_severity': 2, 'symptom_count': 1, 'comorbidities_count': 2, 'cardiac_history': 1, 'diabetes_status': 0, 'respiratory_history': 0, 'chronic_conditions': 2},
]

print("="*100)
print("MULTI-LABEL DEPARTMENT RECOMMENDATIONS - 20 PATIENT TEST")
print("="*100)

engine = MLEngine(model_dir='app/models')

print(f"\n{'ID':<4} {'Age':<5} {'Risk':<8} {'Score':<6} {'Depts':<8} {'Recommended Departments':<50}")
print("-"*100)

multi_label_count = 0
for patient in test_patients:
    patient['visit_id'] = patient['id']
    prediction = engine.predict(patient)
    
    risk = prediction['risk_level']
    score = prediction['risk_score']
    depts = prediction['recommended_departments']
    num_depts = len(depts)
    
    if num_depts > 1:
        multi_label_count += 1
    
    # Format departments for display
    dept_str = ', '.join(depts)
    
    print(f"{patient['id']:<4} {patient['age']:<5} {risk:<8} {score:.2f}   {num_depts:<8} {dept_str:<50}")

print("\n" + "="*100)
print("SUMMARY")
print("="*100)

# Count by risk level
risk_counts = {}
dept_distribution = {}
for patient in test_patients:
    patient['visit_id'] = patient['id']
    prediction = engine.predict(patient)
    risk_counts[prediction['risk_level']] = risk_counts.get(prediction['risk_level'], 0) + 1
    
    for dept in prediction['recommended_departments']:
        dept_distribution[dept] = dept_distribution.get(dept, 0) + 1

print(f"\nRisk Level Distribution:")
for risk, count in sorted(risk_counts.items()):
    print(f"  {risk}: {count}")

print(f"\nDepartment Recommendations (Total):")
for dept, count in sorted(dept_distribution.items(), key=lambda x: x[1], reverse=True):
    print(f"  {dept}: {count}")

print(f"\nMulti-Label Cases: {multi_label_count}/20 ({multi_label_count/20*100:.0f}%)")
print("\n" + "="*100)
