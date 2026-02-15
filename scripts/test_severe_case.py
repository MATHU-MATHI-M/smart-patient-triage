"""
Test the model with a severe case to verify it's now working correctly.
This should classify as HIGH RISK and route to Emergency/Neurology.
"""
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.models.ml_engine import MLEngine
from app.core.database import Database

# Test with a severe case: fractured skull, loss of consciousness
print("="*60)
print("TESTING SEVERE CASE: Fractured Skull + Loss of Consciousness")
print("="*60)

# First, let's see what features we're getting from the DB
db = Database()
features = db.get_visit_features(1)  # Assuming visit_id 1 is the severe case

print("\n📊 Features extracted from database:")
print(json.dumps(features, indent=2))

print("\n🔬 Running ML prediction...")
engine = MLEngine(model_dir='app/models')
prediction = engine.predict(features)

print("\n" + "="*60)
print("PREDICTION RESULT:")
print("="*60)
print(f"Risk Level: {prediction['risk_level']}")
print(f"Risk Score: {prediction['risk_score']:.2f}")
print(f"Recommended Department: {prediction['recommended_department']}")
print("\nDepartment Scores:")
for dept, score in sorted(prediction['department_scores'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {dept}: {score:.3f}")

print("\n" + "="*60)
print("EXPECTED: High Risk, Emergency or Neurology")
print("="*60)
