"""
Test Rule-Based Triage Engine with Real Database Data
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.core.database import Database
from app.models.rule_engine import RuleBasedTriageEngine
import json

def test_visit(visit_id: int):
    """Test a single visit"""
    print(f"\n{'='*80}")
    print(f"TESTING VISIT ID: {visit_id}")
    print(f"{'='*80}\n")
    
    try:
        # Fetch visit data
        visit_data = Database.get_visit_features(visit_id)
        print(f"✅ Fetched visit data")
        print(f"   Chief Complaint: {visit_data.get('chief_complaint')}")
        print(f"   Age: {visit_data.get('age')}")
        print(f"   Symptoms: {len(visit_data.get('symptoms', []))}")
        print(f"   Medical History: {len(visit_data.get('medical_history', []))}")
        
        # Run triage engine
        engine = RuleBasedTriageEngine()
        prediction = engine.predict(visit_data)
        
        print(f"\n📊 TRIAGE RESULTS:")
        print(f"   Risk Level: {prediction['risk_level']}")
        print(f"   Risk Score: {prediction['risk_score']:.4f}")
        print(f"   Primary Department: {prediction['primary_department']}")
        
        print(f"\n🏥 DEPARTMENT SCORES:")
        for dept, score in sorted(prediction['department_scores'].items(), key=lambda x: x[1], reverse=True):
            if score >= 0.35:
                print(f"   {dept}: {score:.3f} ✅")
            else:
                print(f"   {dept}: {score:.3f}")
        
        print(f"\n💡 EXPLAINABILITY:")
        exp = prediction['explainability']
        
        if 'risk_factors' in exp:
            print(f"   Risk Factors:")
            for key, value in exp['risk_factors'].items():
                print(f"      - {key}: {value}")
        
        if 'department_reasoning' in exp:
            print(f"\n   Department Reasoning:")
            for dept, reason in exp['department_reasoning'].items():
                print(f"      - {dept}: {reason}")
        
        if 'score_breakdown' in exp:
            print(f"\n   Score Breakdown:")
            breakdown = exp['score_breakdown']
            print(f"      - Symptom Score: {breakdown.get('symptom_score', 0)}")
            print(f"      - Vitals Score: {breakdown.get('vitals_score', 0)}")
            print(f"      - History Score: {breakdown.get('history_score', 0)}")
            print(f"      - Age Score: {breakdown.get('age_score', 0)}")
            print(f"      - TOTAL: {breakdown.get('total', 0)}")
        
        print(f"\n🎯 CONFIDENCE METRICS:")
        conf = prediction['confidence']
        print(f"   Overall Confidence: {conf['overall']:.3f}")
        print(f"   Data Completeness: {conf['data_completeness']:.3f}")
        print(f"   Decision Clarity: {conf['decision_clarity']:.3f}")
        print(f"   Has Critical Indicators: {conf['has_critical_indicators']}")
        
        # Save full JSON
        output_file = f"visit_{visit_id}_prediction.json"
        with open(output_file, 'w') as f:
            json.dump(prediction, f, indent=2)
        print(f"\n💾 Saved full prediction to {output_file}")
        
        return prediction
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test with sample visit IDs from the database
    test_visits = [1, 2, 4, 9]  # Different scenarios
    
    print("\n" + "="*80)
    print("RULE-BASED TRIAGE ENGINE - DATABASE TEST")
    print("="*80)
    
    results = {}
    for visit_id in test_visits:
        result = test_visit(visit_id)
        if result:
            results[visit_id] = result
    
    print(f"\n\n{'='*80}")
    print(f"SUMMARY: Tested {len(results)}/{len(test_visits)} visits successfully")
    print(f"{'='*80}\n")
