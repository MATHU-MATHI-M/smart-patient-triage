import pandas as pd
import random
from faker import Faker

fake = Faker()
random.seed(42)

patients = pd.read_csv("data_output/patients.csv")

conditions = [
    "Diabetes",
    "Hypertension",
    "Asthma",
    "COPD",
    "Arthritis",
    "Heart Disease",
    "Migraine",
    "Kidney Disease"
]

conditions += [
    "Coronary Artery Disease",
    "Chronic Kidney Disease",
    "Stroke History",
    "Epilepsy",
    "Hypothyroidism",
    "Hyperthyroidism",
    "Depression",
    "Anxiety Disorder",
    "Obesity",
    "Anemia",
    "Gastritis",
    "Peptic Ulcer Disease",
    "Liver Disease",
    "Sleep Apnea",
    "Tuberculosis",
    "Cancer",
    "Parkinson’s Disease",
    "Alzheimer’s Disease",
    "Peripheral Artery Disease",
    "Osteoporosis"
]

rows = []
history_id = 1

for pid in patients["patient_id"]:
    for _ in range(random.randint(1, 4)):
        cond = random.choice(conditions)
        rows.append({
            "history_id": history_id,
            "patient_id": pid,
            "condition_name": cond,
            "is_chronic": True,
            "notes": fake.sentence(),
            "diagnosis_date": fake.date_between("-8y", "today")
        })
        history_id += 1

pd.DataFrame(rows).to_csv(
    "data_output/patient_medical_history.csv", index=False
)

print("Medical history generated.")
