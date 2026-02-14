import os

scripts = [
    #"synthetic_data/generate_dept.py",
    #"synthetic_data/generate_patients.py",
    #"synthetic_data/generate_medical_hist.py",
    #"synthetic_data/generate_visits.py",
    #"synthetic_data/generate_vitals.py",
    "synthetic_data/generate_symptoms.py"
]

for script in scripts:
    os.system(f"python {script}")
