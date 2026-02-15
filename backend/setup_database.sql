-- User Mandated Schema
CREATE TABLE patients (
	patient_id SERIAL PRIMARY KEY,
	full_name VARCHAR(120) NOT NULL,
	age INT CHECK (age >= 0),
	gender VARCHAR(10),
	contact_info VARCHAR(150),
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patient_medical_history (
	history_id SERIAL PRIMARY KEY,
	patient_id INT REFERENCES patients(patient_id) ON DELETE CASCADE,
	condition_name VARCHAR(150),
	is_chronic BOOLEAN DEFAULT FALSE,
	notes TEXT,
	diagnosis_date DATE
);

CREATE TABLE patient_visits (
	visit_id SERIAL PRIMARY KEY,
	patient_id INT REFERENCES patients(patient_id) ON DELETE CASCADE,
	visit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	chief_complaint TEXT,
	visit_status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE vitals (
	vitals_id SERIAL PRIMARY KEY,
	visit_id INT REFERENCES patient_visits(visit_id) ON DELETE CASCADE,
	bp_systolic INT,
	bp_diastolic INT,
	heart_rate INT,
	temperature FLOAT,
	recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE visit_symptoms (
	symptom_id SERIAL PRIMARY KEY,
	visit_id INT REFERENCES patient_visits(visit_id) ON DELETE CASCADE,
	symptom_name VARCHAR(150),
	severity_score INT CHECK (severity_score BETWEEN 1 AND 5),
	duration VARCHAR(50)
);

CREATE TABLE departments (
	dept_id SERIAL PRIMARY KEY,
	dept_name VARCHAR(100) UNIQUE,
	specialty_description TEXT
);

CREATE TABLE triage_predictions (
	prediction_id SERIAL PRIMARY KEY,
	visit_id INT REFERENCES patient_visits(visit_id) ON DELETE CASCADE,
	
	risk_level VARCHAR(10),
	risk_score FLOAT,
	
	recommended_department VARCHAR(100),
	department_scores JSONB,
	explainability JSONB
);

CREATE TABLE department_queue (
	queue_id SERIAL PRIMARY KEY,
	
	prediction_id INT REFERENCES triage_predictions(prediction_id) ON DELETE CASCADE,
	dept_id INT REFERENCES departments(dept_id),
	
	priority_score FLOAT,
	queue_position INT,
	
	status VARCHAR(20) DEFAULT 'pending',
	added_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patient_visit ON patient_visits(patient_id);
CREATE INDEX idx_prediction_visit ON triage_predictions(visit_id);
CREATE INDEX idx_queue_dept ON department_queue(dept_id);
