from faker import Faker
import pandas as pd
import random
from datetime import datetime

fake = Faker()
random.seed(42)

NUM_PATIENTS = 200
patients = []

for pid in range(1, NUM_PATIENTS + 1):
    patients.append({
        "patient_id": pid,
        "full_name": fake.name(),
        "age": random.randint(18, 85),
        "gender": random.choice(["M", "F"]),
        "contact_info": fake.email(),
        "created_at": datetime.now(),
        "updated_at":   datetime.now()
    })

pd.DataFrame(patients).to_csv("data_output/patients.csv", index=False)
print("Patients generated.")
