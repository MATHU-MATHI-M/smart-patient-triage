import json
import pandas as pd
from datetime import datetime

BASE = "."  # run from repo root; data_output is at ./data_output

def parse_datetime(s):
    try:
        pd.to_datetime(s)
        return True
    except Exception:
        return False

def load(path):
    return pd.read_csv(path)

def main():
    violations = {}

    patients = load(f"{BASE}/data_output/patients.csv")
    pmh = load(f"{BASE}/data_output/patient_medical_history.csv")
    visits = load(f"{BASE}/data_output/patient_visits.csv")
    vitals = load(f"{BASE}/data_output/vitals.csv")
    symptoms = load(f"{BASE}/data_output/visit_symptoms.csv")
    depts = load(f"{BASE}/data_output/departments.csv")

    # patients
    p_viol = []
    if patients['patient_id'].duplicated().any():
        p_viol.append('patient_id not unique')
    if patients['patient_id'].isnull().any():
        p_viol.append('patient_id has nulls')
    if patients['full_name'].isnull().any() or (patients['full_name'].astype(str).str.strip()=='').any():
        p_viol.append('full_name missing')
    if (patients['age'] < 0).any():
        p_viol.append('age < 0')
    # created_at / updated_at parseable
    bad_ts = [i for i,s in enumerate(patients['created_at']) if not parse_datetime(s)]
    if bad_ts:
        p_viol.append(f'created_at unparsable rows: {bad_ts[:5]}')
    bad_ts2 = [i for i,s in enumerate(patients['updated_at']) if not parse_datetime(s)]
    if bad_ts2:
        p_viol.append(f'updated_at unparsable rows: {bad_ts2[:5]}')
    if p_viol:
        violations['patients'] = p_viol

    # patient_medical_history
    h_viol = []
    if pmh['history_id'].duplicated().any():
        h_viol.append('history_id not unique')
    missing_patients = sorted(set(pmh['patient_id'].dropna().unique()) - set(patients['patient_id'].dropna().unique()))
    if missing_patients:
        h_viol.append(f'patient_id references missing patients: {missing_patients[:10]}')
    # diagnosis_date parse
    bad_diag = [i for i,s in enumerate(pmh['diagnosis_date']) if not pd.isna(s) and not parse_datetime(s)]
    if bad_diag:
        h_viol.append(f'diagnosis_date unparsable rows: {bad_diag[:5]}')
    violations['patient_medical_history'] = h_viol if h_viol else []

    # patient_visits
    v_viol = []
    if visits['visit_id'].duplicated().any():
        v_viol.append('visit_id not unique')
    missing_patients = sorted(set(visits['patient_id'].dropna().unique()) - set(patients['patient_id'].dropna().unique()))
    if missing_patients:
        v_viol.append(f'patient_id references missing patients: {missing_patients[:10]}')
    bad_visit_ts = [i for i,s in enumerate(visits['visit_timestamp']) if not parse_datetime(s)]
    if bad_visit_ts:
        v_viol.append(f'visit_timestamp unparsable rows: {bad_visit_ts[:5]}')
    violations['patient_visits'] = v_viol

    # vitals
    vt_viol = []
    if vitals['vitals_id'].duplicated().any():
        vt_viol.append('vitals_id not unique')
    missing_visits = sorted(set(vitals['visit_id'].dropna().unique()) - set(visits['visit_id'].dropna().unique()))
    if missing_visits:
        vt_viol.append(f'visit_id references missing visits: {missing_visits[:10]}')
    # numeric checks
    for col in ['bp_systolic','bp_diastolic','heart_rate','temperature']:
        if col not in vitals.columns:
            vt_viol.append(f'missing column {col}')
    bad_rec = [i for i,s in enumerate(vitals['recorded_at']) if not parse_datetime(s)]
    if bad_rec:
        vt_viol.append(f'recorded_at unparsable rows: {bad_rec[:5]}')
    violations['vitals'] = vt_viol

    # visit_symptoms
    vs_viol = []
    if symptoms['symptom_id'].duplicated().any():
        vs_viol.append('symptom_id not unique')
    missing_visits = sorted(set(symptoms['visit_id'].dropna().unique()) - set(visits['visit_id'].dropna().unique()))
    if missing_visits:
        vs_viol.append(f'visit_id references missing visits: {missing_visits[:10]}')
    # severity_score range
    if 'severity_score' in symptoms.columns:
        bad_sev = symptoms[~symptoms['severity_score'].between(1,5)]['symptom_id'].tolist()
        if bad_sev:
            vs_viol.append(f'severity_score out of range symptom_ids: {bad_sev[:10]}')
    violations['visit_symptoms'] = vs_viol

    # departments
    d_viol = []
    if depts['dept_id'].duplicated().any():
        d_viol.append('dept_id not unique')
    if depts['dept_name'].duplicated().any():
        d_viol.append('dept_name not unique')
    violations['departments'] = d_viol

    # Print summary
    print(json.dumps(violations, indent=2))

if __name__ == '__main__':
    main()
