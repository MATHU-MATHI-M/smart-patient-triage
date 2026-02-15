"""
Complete Rule-Based Triage Engine
Replaces ML model with comprehensive medical logic
"""
from typing import Dict, Any, List
import logging

class RuleBasedTriageEngine:
    """Comprehensive rule-based triage system"""
    
    def __init__(self):
        logging.info("✅ Rule-Based Triage Engine initialized")
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main prediction method using comprehensive medical rules
        
        Returns:
            - risk_level: High/Medium/Low
            - risk_score: 0-100 scale
            - primary_department: Main department
            - department_scores: All department scores (0-1 scale)
            - explainability: Detailed reasoning
            - confidence: Confidence metrics
        """
        # Extract all patient data
        symptoms = patient_data.get('symptoms', [])
        vitals = patient_data.get('vitals', {})
        medical_history = patient_data.get('medical_history', [])
        age = patient_data.get('age', 40)
        chief_complaint = str(patient_data.get('chief_complaint', '')).lower()
        
        # 1. SYMPTOM ANALYSIS
        symptom_analysis = self._analyze_symptoms(symptoms, chief_complaint)
        
        # 2. VITALS ANALYSIS
        vitals_analysis = self._analyze_vitals(vitals, age)
        
        # 3. MEDICAL HISTORY ANALYSIS
        history_analysis = self._analyze_medical_history(medical_history, age)
        
        # 4. CALCULATE TOTAL RISK SCORE (0-100)
        risk_score = (
            symptom_analysis['score'] +
            vitals_analysis['score'] +
            history_analysis['score'] +
            self._calculate_age_factor(age)
        )
        
        # 5. DETERMINE RISK LEVEL
        if risk_score >= 60:
            risk_level = 'High'
        elif risk_score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # 6. CALCULATE DEPARTMENT SCORES
        dept_scores = self._calculate_department_scores(
            symptom_analysis,
            vitals_analysis,
            history_analysis,
            chief_complaint,
            risk_score
        )
        
        # 7. DETERMINE PRIMARY DEPARTMENT
        primary_dept = max(dept_scores.items(), key=lambda x: x[1])[0]
        
        # 8. CALCULATE CONFIDENCE
        confidence = self._calculate_confidence(
            symptom_analysis,
            vitals_analysis,
            history_analysis,
            dept_scores
        )
        
        # 9. GENERATE EXPLAINABILITY
        explainability = self._generate_explainability(
            symptom_analysis,
            vitals_analysis,
            history_analysis,
            age,
            risk_score,
            dept_scores,
            primary_dept
        )
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score / 100, 4),  # Normalize to 0-1
            'primary_department': primary_dept,
            'department_scores': dept_scores,
            'explainability': explainability,
            'confidence': confidence
        }
    
    def _analyze_symptoms(self, symptoms: List[Dict], chief_complaint: str) -> Dict[str, Any]:
        """Analyze symptoms and return scoring + details"""
        score = 0
        critical_symptoms = []
        severity_breakdown = {5: [], 4: [], 3: [], 2: [], 1: []}
        
        # Analyze each symptom
        for symptom in symptoms:
            name = symptom.get('symptom_name', '').lower()
            severity = symptom.get('severity_score', 0)
            
            # Add to severity breakdown
            if severity in severity_breakdown:
                severity_breakdown[severity].append(name)
            
            # Score based on severity
            if severity == 5:
                score += 10
                critical_symptoms.append(f"{name} (severity 5)")
            elif severity == 4:
                score += 7
            elif severity == 3:
                score += 5
            elif severity == 2:
                score += 3
            elif severity == 1:
                score += 1
            
            # CRITICAL SYMPTOM BONUSES
            if 'chest pain' in name:
                score += 15
                if name not in critical_symptoms:
                    critical_symptoms.append(f"{name} (CARDIAC ALERT)")
            
            if any(word in name for word in ['seizure', 'convulsion']):
                score += 15
                if name not in critical_symptoms:
                    critical_symptoms.append(f"{name} (NEURO ALERT)")
            
            if 'loss of consciousness' in name or 'unconscious' in name:
                score += 15
                if name not in critical_symptoms:
                    critical_symptoms.append(f"{name} (CRITICAL)")
            
            if any(word in name for word in ['shortness of breath', 'difficulty breathing', 'dyspnea']):
                score += 12
                if name not in critical_symptoms:
                    critical_symptoms.append(f"{name} (RESPIRATORY ALERT)")
        
        # Cap symptom score at 40
        score = min(score, 40)
        
        return {
            'score': score,
            'critical_symptoms': critical_symptoms,
            'severity_breakdown': severity_breakdown,
            'total_symptoms': len(symptoms),
            'has_chest_pain': any('chest pain' in s.get('symptom_name', '').lower() for s in symptoms),
            'has_seizures': any('seizure' in s.get('symptom_name', '').lower() for s in symptoms),
            'has_respiratory': any(word in s.get('symptom_name', '').lower() for s in symptoms for word in ['breath', 'dyspnea', 'cough']),
            'has_neuro': any(word in s.get('symptom_name', '').lower() for s in symptoms for word in ['dizziness', 'headache', 'numbness', 'tingling', 'seizure'])
        }
    
    def _analyze_vitals(self, vitals: Dict, age: int) -> Dict[str, Any]:
        """Analyze vital signs and return scoring + details"""
        score = 0
        abnormal_vitals = []
        
        bp_sys = vitals.get('bp_systolic', 120)
        bp_dia = vitals.get('bp_diastolic', 80)
        hr = vitals.get('heart_rate', 80)
        temp = vitals.get('temperature', 98.6)
        
        # BP SYSTOLIC
        if bp_sys >= 180:
            score += 10
            abnormal_vitals.append(f"BP {bp_sys}/{bp_dia} (HYPERTENSIVE CRISIS)")
        elif bp_sys >= 160:
            score += 7
            abnormal_vitals.append(f"BP {bp_sys}/{bp_dia} (Stage 2 Hypertension)")
        elif bp_sys >= 140:
            score += 5
            abnormal_vitals.append(f"BP {bp_sys}/{bp_dia} (Stage 1 Hypertension)")
        elif bp_sys < 90:
            score += 8
            abnormal_vitals.append(f"BP {bp_sys}/{bp_dia} (HYPOTENSION)")
        
        # BP DIASTOLIC
        if bp_dia >= 110:
            score += 8
            if not any('BP' in v for v in abnormal_vitals):
                abnormal_vitals.append(f"BP {bp_sys}/{bp_dia} (CRITICAL)")
        elif bp_dia >= 100:
            score += 5
        elif bp_dia >= 90:
            score += 3
        
        # HEART RATE
        if hr >= 120:
            score += 10
            abnormal_vitals.append(f"HR {hr} (SEVERE TACHYCARDIA)")
        elif hr >= 100:
            score += 7
            abnormal_vitals.append(f"HR {hr} (Tachycardia)")
        elif hr < 60:
            score += 5
            abnormal_vitals.append(f"HR {hr} (Bradycardia)")
        
        # TEMPERATURE
        if temp >= 102:
            score += 8
            abnormal_vitals.append(f"Temp {temp}°F (HIGH FEVER)")
        elif temp >= 100:
            score += 5
            abnormal_vitals.append(f"Temp {temp}°F (Fever)")
        elif temp < 96:
            score += 5
            abnormal_vitals.append(f"Temp {temp}°F (Hypothermia)")
        
        # Cap vitals score at 30
        score = min(score, 30)
        
        return {
            'score': score,
            'abnormal_vitals': abnormal_vitals,
            'bp_systolic': bp_sys,
            'bp_diastolic': bp_dia,
            'heart_rate': hr,
            'temperature': temp,
            'has_critical_bp': bp_sys >= 180 or bp_dia >= 110,
            'has_critical_hr': hr >= 120 or hr < 50,
            'has_fever': temp >= 100
        }
    
    def _analyze_medical_history(self, history: List[Dict], age: int) -> Dict[str, Any]:
        """Analyze medical history and return scoring + details"""
        score = 0
        conditions = []
        cardiac_conditions = []
        respiratory_conditions = []
        neuro_conditions = []
        chronic_count = 0
        
        for item in history:
            condition = item.get('condition_name', '').lower()
            is_chronic = item.get('is_chronic', False)
            
            conditions.append(condition)
            if is_chronic:
                chronic_count += 1
                score += 2
            
            # CARDIAC CONDITIONS
            if any(word in condition for word in ['coronary', 'heart', 'cardiac', 'hypertension', 'arrhythmia']):
                score += 8
                cardiac_conditions.append(condition.title())
            
            # RESPIRATORY CONDITIONS
            if any(word in condition for word in ['copd', 'asthma', 'tuberculosis', 'respiratory', 'lung']):
                score += 6
                respiratory_conditions.append(condition.title())
            
            # NEUROLOGICAL CONDITIONS
            if any(word in condition for word in ['epilepsy', 'seizure', 'parkinson', 'stroke', 'alzheimer']):
                score += 7
                neuro_conditions.append(condition.title())
            
            # DIABETES
            if 'diabetes' in condition:
                score += 5
        
        # Cap history score at 20
        score = min(score, 20)
        
        return {
            'score': score,
            'conditions': conditions,
            'cardiac_conditions': cardiac_conditions,
            'respiratory_conditions': respiratory_conditions,
            'neuro_conditions': neuro_conditions,
            'chronic_count': chronic_count,
            'has_cardiac_history': len(cardiac_conditions) > 0,
            'has_respiratory_history': len(respiratory_conditions) > 0,
            'has_neuro_history': len(neuro_conditions) > 0
        }
    
    def _calculate_age_factor(self, age: int) -> int:
        """Calculate age-based risk adjustment"""
        if age >= 80:
            return 10
        elif age >= 70:
            return 7
        elif age >= 60:
            return 5
        elif age <= 5:
            return 8
        elif age <= 12:
            return 5
        else:
            return 0
    
    def _calculate_department_scores(
        self,
        symptom_analysis: Dict,
        vitals_analysis: Dict,
        history_analysis: Dict,
        chief_complaint: str,
        total_risk: float
    ) -> Dict[str, float]:
        """Calculate scores for each department (0-1 scale)"""
        
        scores = {
            'Emergency': 0.10,
            'Cardiology': 0.05,
            'Neurology': 0.05,
            'Respiratory': 0.05,
            'Orthopedics': 0.05,
            'General Medicine': 0.20
        }
        
        # EMERGENCY
        if symptom_analysis['critical_symptoms']:
            scores['Emergency'] += 0.30
        if vitals_analysis['has_critical_bp'] or vitals_analysis['has_critical_hr']:
            scores['Emergency'] += 0.25
        if total_risk >= 70:
            scores['Emergency'] += 0.20
        if any(sev5 for sev5 in symptom_analysis['severity_breakdown'][5]):
            scores['Emergency'] += 0.15
        
        # CARDIOLOGY
        if symptom_analysis['has_chest_pain']:
            scores['Cardiology'] += 0.40
            chest_pain_severity = max([s.get('severity_score', 0) for s in symptom_analysis.get('raw_symptoms', []) if 'chest pain' in s.get('symptom_name', '').lower()] or [0])
            if chest_pain_severity >= 4:
                scores['Cardiology'] += 0.30
        if history_analysis['has_cardiac_history']:
            scores['Cardiology'] += 0.25
        if vitals_analysis['bp_systolic'] >= 160 or vitals_analysis['heart_rate'] >= 100:
            scores['Cardiology'] += 0.20
        
        # NEUROLOGY
        if symptom_analysis['has_seizures']:
            scores['Neurology'] += 0.45
        if symptom_analysis['has_neuro']:
            scores['Neurology'] += 0.25
        if history_analysis['has_neuro_history']:
            scores['Neurology'] += 0.25
        if any(word in chief_complaint for word in ['head', 'skull', 'brain', 'stroke']):
            scores['Neurology'] += 0.20
        
        # RESPIRATORY
        if symptom_analysis['has_respiratory']:
            scores['Respiratory'] += 0.40
        if history_analysis['has_respiratory_history']:
            scores['Respiratory'] += 0.30
        if vitals_analysis['has_fever'] and symptom_analysis['has_respiratory']:
            scores['Respiratory'] += 0.25
        
        # ORTHOPEDICS
        if any(word in chief_complaint for word in ['joint', 'bone', 'fracture', 'back pain', 'neck pain']):
            scores['Orthopedics'] += 0.35
        if 'arthritis' in str(history_analysis['conditions']).lower():
            scores['Orthopedics'] += 0.20
        
        # GENERAL MEDICINE
        if total_risk < 40:
            scores['General Medicine'] += 0.25
        if history_analysis['chronic_count'] >= 2:
            scores['General Medicine'] += 0.20
        
        # Normalize scores to max 1.0
        for dept in scores:
            scores[dept] = min(scores[dept], 1.0)
        
        return scores
    
    def _calculate_confidence(
        self,
        symptom_analysis: Dict,
        vitals_analysis: Dict,
        history_analysis: Dict,
        dept_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate confidence metrics"""
        
        # Data completeness
        has_symptoms = symptom_analysis['total_symptoms'] > 0
        has_vitals = len(vitals_analysis['abnormal_vitals']) > 0 or True  # Always have vitals
        has_history = len(history_analysis['conditions']) > 0
        
        data_completeness = sum([has_symptoms, has_vitals, has_history]) / 3.0
        
        # Decision clarity (how distinct is top department from others)
        sorted_scores = sorted(dept_scores.values(), reverse=True)
        if len(sorted_scores) >= 2:
            score_separation = sorted_scores[0] - sorted_scores[1]
        else:
            score_separation = 0.5
        
        # Overall confidence
        overall_confidence = (data_completeness * 0.6) + (score_separation * 0.4)
        
        return {
            'overall': round(overall_confidence, 3),
            'data_completeness': round(data_completeness, 3),
            'decision_clarity': round(score_separation, 3),
            'has_critical_indicators': len(symptom_analysis['critical_symptoms']) > 0 or vitals_analysis['has_critical_bp']
        }
    
    def _generate_explainability(
        self,
        symptom_analysis: Dict,
        vitals_analysis: Dict,
        history_analysis: Dict,
        age: int,
        risk_score: float,
        dept_scores: Dict[str, float],
        primary_dept: str
    ) -> Dict[str, Any]:
        """Generate detailed explainability"""
        
        # Risk factors
        risk_factors = {}
        
        if symptom_analysis['critical_symptoms']:
            risk_factors['critical_symptoms'] = symptom_analysis['critical_symptoms']
        
        if vitals_analysis['abnormal_vitals']:
            risk_factors['abnormal_vitals'] = vitals_analysis['abnormal_vitals']
        
        if history_analysis['cardiac_conditions']:
            risk_factors['cardiac_history'] = history_analysis['cardiac_conditions']
        if history_analysis['respiratory_conditions']:
            risk_factors['respiratory_history'] = history_analysis['respiratory_conditions']
        if history_analysis['neuro_conditions']:
            risk_factors['neurological_history'] = history_analysis['neuro_conditions']
        
        if age >= 70 or age <= 12:
            risk_factors['age_factor'] = f"{age} years ({'elderly' if age >= 70 else 'pediatric'})"
        
        # Department reasoning
        dept_reasoning = {}
        for dept, score in sorted(dept_scores.items(), key=lambda x: x[1], reverse=True)[:3]:
            if score >= 0.35:
                reasons = []
                
                if dept == 'Emergency':
                    if symptom_analysis['critical_symptoms']:
                        reasons.append("Critical symptoms present")
                    if vitals_analysis['has_critical_bp'] or vitals_analysis['has_critical_hr']:
                        reasons.append("Critical vital signs")
                    if risk_score >= 70:
                        reasons.append("High overall risk score")
                
                elif dept == 'Cardiology':
                    if symptom_analysis['has_chest_pain']:
                        reasons.append("Chest pain reported")
                    if history_analysis['has_cardiac_history']:
                        reasons.append(f"Cardiac history: {', '.join(history_analysis['cardiac_conditions'][:2])}")
                    if vitals_analysis['bp_systolic'] >= 160:
                        reasons.append("Elevated blood pressure")
                
                elif dept == 'Neurology':
                    if symptom_analysis['has_seizures']:
                        reasons.append("Seizures present")
                    if symptom_analysis['has_neuro']:
                        reasons.append("Neurological symptoms")
                    if history_analysis['has_neuro_history']:
                        reasons.append(f"Neuro history: {', '.join(history_analysis['neuro_conditions'][:2])}")
                
                elif dept == 'Respiratory':
                    if symptom_analysis['has_respiratory']:
                        reasons.append("Respiratory symptoms")
                    if history_analysis['has_respiratory_history']:
                        reasons.append(f"Respiratory history: {', '.join(history_analysis['respiratory_conditions'][:2])}")
                
                if reasons:
                    dept_reasoning[dept] = " + ".join(reasons)
        
        # Score breakdown
        score_breakdown = {
            'symptom_score': symptom_analysis['score'],
            'vitals_score': vitals_analysis['score'],
            'history_score': history_analysis['score'],
            'age_score': self._calculate_age_factor(age),
            'total': round(risk_score, 1)
        }
        
        return {
            'risk_factors': risk_factors,
            'department_reasoning': dept_reasoning,
            'score_breakdown': score_breakdown
        }
