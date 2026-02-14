import pandas as pd
import random

visits = pd.read_csv("data_output/patient_visits.csv")

symptoms_master = [
    "Chest pain",
    "Shortness of breath",
    "Cough",
    "Fever",
    "Headache",
    "Nausea",
    "Fatigue",
    "Wheezing",
    "Dizziness"
]

symptoms_master += [
    "Abdominal pain",
    "Vomiting",
    "Diarrhea",
    "Palpitations",
    "Loss of consciousness",
    "Seizures",
    "Blurred vision",
    "Double vision",
    "Joint pain",
    "Muscle weakness",
    "Numbness",
    "Tingling sensation",
    "Skin rash",
    "Itching",
    "Swelling in legs",
    "Weight loss",
    "Weight gain",
    "Loss of appetite",
    "Persistent cough",
    "Sore throat",
    "Ear pain",
    "Burning urination",
    "Frequent urination",
    "Night sweats",
    "Chills",
    "Back stiffness",
    "Neck pain",
    "Hoarseness",
    "Chest tightness",
    "Excessive sweating"
]

rows = []
symptom_id = 1

for vid in visits["visit_id"]:
    for _ in range(random.randint(2, 5)):
        rows.append({
            "symptom_id": symptom_id,
            "visit_id": vid,
            "symptom_name": random.choice(symptoms_master),
            "severity_score": random.randint(1, 5),
            "duration": random.choice(
                ["1 hour", "3 hours", "6 hours", "1 day", "2 days"]
            )
        })
        symptom_id += 1

pd.DataFrame(rows).to_csv("data_output/visit_symptoms.csv", index=False)
print("Symptoms generated.")
