import pandas as pd
import random
from faker import Faker
from datetime import datetime

fake = Faker()
random.seed(42)

patients = pd.read_csv("data_output/patients.csv")

NUM_VISITS = 500

complaints = [
    "Chest pain",
    "Shortness of breath",
    "Fever",
    "Headache",
    "Back pain",
    "Fatigue",
    "Dizziness"
]

complaints += [
    "Abdominal pain",
    "Vomiting",
    "Diarrhea",
    "Palpitations",
    "Loss of consciousness",
    "Seizure episode",
    "Joint pain",
    "Swelling in legs",
    "Blurred vision",
    "Skin rash",
    "Burning urination",
    "Frequent urination",
    "Weight loss",
    "Weight gain",
    "Persistent cough",
    "Sore throat",
    "Ear pain",
    "Numbness in limbs",
    "Weakness",
    "Loss of appetite"
]

visits = []

for vid in range(1, NUM_VISITS + 1):
    visits.append({
        "visit_id": vid,
        "patient_id": random.choice(patients["patient_id"].tolist()),
        "visit_timestamp": 
          #random datetime between 1 month and now
            fake.date_time_between(start_date="-1M", end_date="now"),

        "chief_complaint": random.choice(complaints),
        "visit_status": "active"
    })

pd.DataFrame(visits).to_csv("data_output/patient_visits.csv", index=False)
print("Visits generated.")
