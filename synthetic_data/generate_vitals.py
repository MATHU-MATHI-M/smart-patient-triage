import pandas as pd
import random
from datetime import datetime

visits = pd.read_csv("data_output/patient_visits.csv")

rows = []

for i, vid in enumerate(visits["visit_id"], start=1):
    rows.append({
        "vitals_id": i,
        "visit_id": vid,
        "bp_systolic": random.randint(100, 170),
        "bp_diastolic": random.randint(60, 110),
        "heart_rate": random.randint(60, 130),
        "temperature": round(random.uniform(97, 102), 1),
        "recorded_at": datetime.now()
    })

pd.DataFrame(rows).to_csv("data_output/vitals.csv", index=False)
print("Vitals generated.")
