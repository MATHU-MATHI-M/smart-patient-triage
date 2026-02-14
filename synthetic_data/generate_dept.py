import pandas as pd

departments = [
    [1, "Emergency", "Acute life-threatening conditions"],
    [2, "Cardiology", "Heart conditions, chest pain"],
    [3, "Respiratory", "Lung conditions, COPD, asthma"],
    [4, "Neurology", "Stroke, seizures, headaches"],
    [5, "General Medicine", "Primary care, infections"],
    [6, "Orthopedics", "Fractures, joint pain"]
]

df = pd.DataFrame(
    departments,
    columns=["dept_id", "dept_name", "specialty_description"]
)

df.to_csv("data_output/departments.csv", index=False)
print("Departments CSV generated.")
