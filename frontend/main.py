import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Triage Dashboard", layout="wide")

# Patient Lookup + Create Flow
st.title("🏥 AI Patient Triage System")
st.header("👤 Patient Data Entry")

# Step 1: Search Logic by ID
# Step 1: Search Logic by Name & Email
col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
search_name = col_s1.text_input("Name (Full/Partial)")
search_email = col_s2.text_input("Email ID")
do_search = col_s3.button("🔍 Search", type="primary")

if do_search:
    # Clear previous state
    if 'selected_patient' in st.session_state: del st.session_state.selected_patient
    if 'patient_history' in st.session_state: del st.session_state.patient_history
    st.session_state.create_patient_mode = False
    
    if search_name or search_email:
        try:
            params = {}
            if search_name: params['name'] = search_name
            if search_email: params['email'] = search_email
            
            resp = requests.get(f"{API_URL}/patients/lookup", params=params)
            
            if resp.status_code == 200:
                results = resp.json().get("patients", [])
                if results:
                    patient = results[0]  # Take first match
                    st.session_state.selected_patient = patient
                    # Fetch History
                    h_resp = requests.get(f"{API_URL}/patients/{patient['patient_id']}/history")
                    if h_resp.status_code == 200:
                        st.session_state.patient_history = h_resp.json().get("history", [])
                    st.success(f"✅ Found: {patient['full_name']} ({patient['contact_info']})")
                    st.rerun()
                else:
                    st.warning("❌ Patient not found. Please Register.")
                    st.session_state.create_patient_mode = True
                    # Pre-fill cache for registration
                    st.session_state.p_name_cache = search_name
                    st.session_state.p_email_cache = search_email
                    st.rerun()
            else:
                st.error(f"Search Error: {resp.text}")
        except Exception as e:
            st.error(f"Connection Failed: {e}")
    else:
        st.warning("Enter Name or Email to search.")

# Manual Creation Form (If ID not found)
if st.session_state.get("create_patient_mode", False):
    st.subheader("🆕 New Patient Registration (Mandatory)")
    with st.form("new_patient_form"):
        col1, col2 = st.columns(2)
        new_name = col1.text_input("Full Name", value=st.session_state.get('p_name_cache', ''))
        new_age = col2.number_input("Age", 0, 120, 30)
        
        col3, col4 = st.columns(2)
        new_gender = col3.selectbox("Gender", ["Male", "Female", "Other"])
        new_contact = col4.text_input("Email ID", value=st.session_state.get('p_email_cache', ''))

        st.markdown("#### 📜 Medical History (MANDATORY)")
        st.info("Please enter at least one history item.")
        
        # Initialize DF
        if 'history_editor_df' not in st.session_state:
            st.session_state.history_editor_df = pd.DataFrame(
                columns=["Condition", "Chronic?", "Notes", "Date"]
            )

        edited_df = st.data_editor(
            st.session_state.history_editor_df,
            num_rows="dynamic",
            column_config={
                "Condition": st.column_config.TextColumn("Condition", required=True),
                "Chronic?": st.column_config.CheckboxColumn("Chronic?", default=False),
                "Notes": st.column_config.TextColumn("Notes"),
                "Date": st.column_config.DateColumn("Diagnosis Date", required=True)
            },
            key="history_editor"
        )
        
        if st.form_submit_button("Register & Start Visit"):
            # Validate History
            history_list = []
            for idx, row in edited_df.iterrows():
                if row["Condition"]:
                    history_list.append({
                        "condition_name": row["Condition"],
                        "is_chronic": row["Chronic?"],
                        "notes": row["Notes"],
                        "diagnosis_date": str(row["Date"]) if row["Date"] else None
                    })
            
            if not history_list:
                st.error("⚠️ medical history is mandatory!")
            else:
                try:
                    payload = {
                        "full_name": new_name, "age": new_age, "gender": new_gender,
                        "contact_info": new_contact,
                        "medical_history": history_list
                    }
                    resp = requests.post(f"{API_URL}/patients", json=payload)
                    if resp.status_code == 200:
                        new_p_data = resp.json()
                        st.session_state.selected_patient = {
                            "patient_id": new_p_data["patient_id"],
                            "full_name": new_name, "age": new_age, "gender": new_gender, "contact_info": new_contact
                        }
                        st.session_state.patient_history = history_list
                        st.session_state.create_patient_mode = False
                        st.success("✅ Patient Registered! Proceed to Triage.")
                        st.rerun()
                    else:
                        st.error(f"Failed to register: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

# Step 2: Patient details form (New OR Selected)
if 'selected_patient' in st.session_state:
    st.divider()
    patient_data = st.session_state.selected_patient
    st.markdown(f"### 📋 Visit Details for: **{patient_data['full_name']}** (ID: `{patient_data['patient_id']}`)")
    
    # Show History
    hist = st.session_state.get('patient_history', [])
    st.markdown("#### 📜 Patient Medical History")
    if hist:
        # Display as a clean DataFrame
        hist_df = pd.DataFrame(hist)
        
        # Cleanup column names for display
        if not hist_df.empty:
            # Filter and rename useful columns
            display_cols = ["condition_name", "is_chronic", "notes", "diagnosis_date"]
            # Ensure columns exist (in case API returns partial)
            cols_to_show = [c for c in display_cols if c in hist_df.columns]
            
            st.dataframe(
                hist_df[cols_to_show].style.format({"is_chronic": lambda x: "✅ Yes" if x else "No"}),
                use_container_width=True,
                column_config={
                    "condition_name": "Condition",
                    "is_chronic": "Chronic?",
                    "notes": "Notes",
                    "diagnosis_date": "Diagnosis Date"
                }
            )
        else:
             st.info("No medical history items found.")
    else:
        st.info("No medical history recorded.")
    
    if st.button("Change Patient"):
        del st.session_state.selected_patient
        if 'patient_history' in st.session_state: del st.session_state.patient_history
        st.rerun()

    # Manual input fields
    st.subheader("🏥 New Visit Data")
    chief_complaint = st.text_input("Chief complaint", "Chest pain")
    
    col1, col2, col3, col4 = st.columns(4)
    bp_systolic = col1.number_input("BP Systolic", 80, 250, 120)
    bp_diastolic = col2.number_input("BP Diastolic", 50, 150, 80)
    heart_rate = col3.number_input("Heart Rate", 40, 200, 80)
    temperature = col4.number_input("Temperature", 95.0, 105.0, 98.6, 0.1)
    
    st.markdown("#### ⚠️ Symptoms")
    symptom_list = []
    
    # Dynamic symptom adder (simple version)
    with st.expander("Add Symptoms", expanded=True):
        s_name = st.selectbox("Symptom", ["Chest Pain", "Shortness of Breath", "Fever", "Dizziness", "Nausea", "Headache"])
        s_severity = st.slider("Severity (1-10)", 1, 10, 5)
        s_duration = st.text_input("Duration", "1 hour")
        if st.checkbox("Confirm Symptom Entry"):
            symptom_list.append({
                "symptom_name": s_name,
                "severity_score": s_severity,
                "duration": s_duration
            })
            st.write(f"Added: {s_name} ({s_severity}/10)")
    
    if st.button("🚀 SUBMIT FOR TRIAGE", type="primary"):
        # POST to backend
        visit_data = {
            "patient_id": patient_data["patient_id"],
            "chief_complaint": chief_complaint,
            "bp_systolic": bp_systolic,
            "bp_diastolic": bp_diastolic,
            "heart_rate": heart_rate,
            "temperature": temperature,
            "symptoms": symptom_list
        }
        
        response = requests.post(f"{API_URL}/patient-visits", json=visit_data)
        if response.status_code == 200:
            st.success("✅ Patient triaged! Check department queues.")
            # Clear selection to reset flow? Or keep?
            # st.rerun() 
        else:
            try:
                err = response.json().get("detail", response.text)
            except:
                err = response.text
            st.error(f"❌ Failed to triage patient: {err}")

# Step 3: View Department Queues
st.subheader("📊 Department Priority Queues")
dept_name = st.selectbox("Select Department", ["Emergency", "Cardiology", "Neurology", "General Medicine"])
if dept_name:
    try:
        response = requests.get(f"{API_URL}/queues/{dept_name}")
        if response.status_code == 200:
            queue = response.json().get("queue", [])
            
            if queue:
                for i, queue_item in enumerate(queue):
                    try:
                        # NEW SCHEMA STRUCTURE:
                        # queue_item (department_queue)
                        # -> triage_predictions (prediction)
                        #    -> patient_visits (visit)
                        #       -> patients (patient) - mapped as object, not list
                        
                        pred = queue_item.get('triage_predictions', {})
                        visit = pred.get('patient_visits', {})
                        patient = visit.get('patients', {})
                        
                        p_name = patient.get('full_name', 'Unknown')
                        complaint = visit.get('chief_complaint', 'No Data')
                        
                        risk_level = pred.get('risk_level', 'Unknown')
                        risk_score = pred.get('risk_score', 0.0)
                        
                        dept_scores = pred.get('department_scores') or {}
                        explain = pred.get('explainability') or {}
                        
                    except Exception as ex:
                        st.error(f"Mapping Error: {ex}")
                        continue
            
                    # Display Card
                    with st.container():
                        c1, c2, c3 = st.columns([1, 4, 2])
                        with c1:
                            st.metric("Priority", f"{queue_item['priority_score']:.2f}")
                        with c2:
                            color = "🔴" if risk_level == "High" else "🟡" if risk_level == "Medium" else "🟢"
                            st.markdown(f"### {color} {p_name}")
                            st.caption(f"**Complaint:** {complaint}")
                            st.caption(f"**Risk:** {risk_level} ({int(risk_score*100)}%)")
                        with c3:
                             st.info(f"Status: {queue_item['status']}")

                        # Details Expander
                        with st.expander(f"📉 AI Analysis for {p_name}"):
                            d_col, e_col = st.columns(2)
                            
                            with d_col:
                                st.markdown("#### 🏥 Dept Scores")
                                # Sort dept scores
                                sorted_depts = sorted(dept_scores.items(), key=lambda x: x[1], reverse=True)
                                for d, s in sorted_depts:
                                    if s > 0.01:
                                        st.progress(s, text=f"{d}: {int(s*100)}%")
                            
                            with e_col:
                                st.markdown("#### 🔍 Explainability")
                                for factor, weight in explain.items():
                                    st.markdown(f"- **{factor}**: (+{int(weight*100)}%)")
                        st.divider()

            else:
                st.info("No patients in queue")
        else:
            try:
                error_detail = response.json().get("detail", response.text)
            except:
                error_detail = response.text
            st.error(f"Backend Error: {error_detail}")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")

