"""
Test script to see what data we're actually getting from the database
for a real patient visit.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

from app.core.database import Database
import json

db = Database()

# Test with visit_id 1 (the fractured skull patient)
print("Fetching features for visit_id 1...")
features = db.get_visit_features(1)

print("\n" + "="*60)
print("FEATURES EXTRACTED FROM DATABASE:")
print("="*60)
print(json.dumps(features, indent=2))

print("\n" + "="*60)
print("CRITICAL FEATURES FOR SEVERE CASE:")
print("="*60)
print(f"max_severity: {features.get('max_severity')}")
print(f"symptom_count: {features.get('symptom_count')}")
print(f"chief_complaint: {features.get('chief_complaint')}")
print(f"comorbidities_count: {features.get('comorbidities_count', 'MISSING!')}")
print(f"cardiac_history: {features.get('cardiac_history', 'MISSING!')}")
