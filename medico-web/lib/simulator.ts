
import { api } from './api';

const FIRST_NAMES_MALE = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles'];
const FIRST_NAMES_FEMALE = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen'];
const LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'];

const CONDITIONS = [
    { name: 'Hypertension', chronic: true },
    { name: 'Type 2 Diabetes', chronic: true },
    { name: 'Asthma', chronic: true },
    { name: 'None', chronic: false },
    { name: 'None', chronic: false },
    { name: 'None', chronic: false }, // Weight towards healthy history
    { name: 'COPD', chronic: true },
    { name: 'Coronary Artery Disease', chronic: true },
    { name: 'Hyperlipidemia', chronic: true },
];

const SYMPTOMS = [
    { name: 'Chest Pain', sevRange: [3, 5], duration: '2 hours', dept: 'Cardiology' },
    { name: 'Shortness of Breath', sevRange: [2, 5], duration: '1 day', dept: 'Respiratory' },
    { name: 'Severe Headache', sevRange: [2, 4], duration: '3 days', dept: 'Neurology' },
    { name: 'High Fever', sevRange: [3, 5], duration: '2 days', dept: 'General Medicine' },
    { name: 'Abdominal Pain', sevRange: [2, 5], duration: '4 hours', dept: 'General Medicine' },
    { name: 'Dizziness', sevRange: [1, 3], duration: 'Morning', dept: 'Neurology' },
    { name: 'Palpitations', sevRange: [2, 4], duration: '30 mins', dept: 'Cardiology' },
    { name: 'Cough', sevRange: [1, 3], duration: '1 week', dept: 'Respiratory' },
];

function randomInt(min: number, max: number) {
    return Math.floor(Math.random() * (max - min + 1) + min);
}

function randomItem<T>(arr: T[]): T {
    return arr[randomInt(0, arr.length - 1)];
}

export async function simulatePatient() {
    try {
        // 1. Create Patient
        const gender = Math.random() > 0.5 ? 'Male' : 'Female';
        const age = randomInt(18, 90);

        const fname = gender === 'Male'
            ? `${randomItem(FIRST_NAMES_MALE)} ${randomItem(LAST_NAMES)}`
            : `${randomItem(FIRST_NAMES_FEMALE)} ${randomItem(LAST_NAMES)}`;

        // Medical History
        const history: any[] = [];
        if (Math.random() > 0.4) { // 60% chance of healthy history
            const numConds = randomInt(1, 2);
            for (let i = 0; i < numConds; i++) {
                const cond = randomItem(CONDITIONS);
                if (cond.name !== 'None') {
                    // prevent dupes
                    if (!history.some(h => h.condition_name === cond.name)) {
                        history.push({
                            condition_name: cond.name,
                            is_chronic: cond.chronic,
                            notes: 'Patient reports history of ' + cond.name,
                            diagnosis_date: '2020-01-01'
                        });
                    }
                }
            }
        }

        const contact = `${fname.toLowerCase().replace(' ', '.')}@example.com`;

        const pRes = await api.post('/patients', {
            full_name: fname,
            age: age,
            gender: gender,
            contact_info: contact,
            medical_history: history
        });

        const pid = pRes.data.patient_id;

        // 2. Create Visit
        const symptom = randomItem(SYMPTOMS);
        let severity = randomInt(symptom.sevRange[0], symptom.sevRange[1]);

        // Vitals based on symptom intensity
        let sys = 120 + randomInt(-10, 40);
        let dia = 80 + randomInt(-10, 20);
        let hr = 80 + randomInt(-10, 40);
        let temp = 98.6 + (Math.random() * 2);

        if (symptom.name === 'Chest Pain' || Math.random() > 0.6) {
            sys += 50;
            hr += 35;
            severity = 5;
        }
        if (symptom.name === 'Fever') {
            temp += 4; hr += 25;
        }

        await api.post('/patient-visits', {
            patient_id: pid,
            chief_complaint: `${symptom.name} for ${symptom.duration}`,
            bp_systolic: sys,
            bp_diastolic: dia,
            heart_rate: hr,
            temperature: parseFloat(temp.toFixed(1)),
            symptoms: [
                { symptom_name: symptom.name, severity_score: severity, duration: symptom.duration }
            ]
        });

        return true;
    } catch (e) {
        console.error("Simulation failed", e);
        return false;
    }
}
