import streamlit as st
import requests
import sqlite3
import pandas as pd
import json
from fpdf import FPDF

# --- CLOUD CONFIGURATION & SECURITY ---
API_URL = "https://cile-cloud.onrender.com/analyze"
INTERNAL_KEY = "INTERNAL_INTERCEPTS"

st.set_page_config(page_title="CILE Workstation", layout="wide")

# --- PDF GENERATION ENGINE ---
def generate_clinical_pdf(report):
    pdf = FPDF()
    pdf.set_margins(left=10, top=10, right=10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    def pdf_safe(text):
        if text is None: return ""
        # Strip emojis to prevent FPDF latin-1 compilation crashes
        clean = str(text).replace('⚠️', '').replace('📌', '').replace('💊', '').replace('🧬', '').replace('🔍', '')
        clean = clean.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'").replace('—', '-').replace('–', '-')
        return clean.encode('latin-1', 'replace').decode('latin-1')

    # Header
    pdf.set_font("helvetica", style="B", size=16)
    pdf.set_x(10)
    pdf.cell(0, 10, "CILE Clinical Consultation Report", ln=1, align="C")
    pdf.line(10, 20, 200, 20)
    pdf.ln(5)
    
    # Demographics
    meta = report.get("report_metadata", {})
    pdf.set_font("helvetica", style="B", size=12)
    pdf.set_x(10)
    pdf.cell(0, 10, "Patient Vitals & Demographics", ln=1)
    pdf.set_font("helvetica", size=10)
    pdf.set_x(10)
    pdf.cell(0, 6, text=pdf_safe(f"Age: {meta.get('patient_age')} | Gender: {meta.get('gender')}"), ln=1)
    pdf.set_x(10)
    pdf.cell(0, 6, text=pdf_safe(f"Weight: {meta.get('weight_kg')} kg | SrCr: {meta.get('serum_creatinine_mgdl')} mg/dL"), ln=1)
    pdf.set_x(10)
    pdf.cell(0, 6, text=pdf_safe(f"Estimated CrCl: {meta.get('estimated_crcl_mlmin')} mL/min"), ln=1)
    pdf.ln(5)
    
    # Renal Alerts
    renal = report.get("renal_alerts", [])
    if renal:
        pdf.set_font("helvetica", style="B", size=12)
        pdf.set_text_color(200, 0, 0)
        pdf.set_x(10)
        pdf.cell(0, 10, "Renal Dose Adjustments Required", ln=1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", size=10)
        for r in renal:
            pdf.set_x(10)
            pdf.multi_cell(w=0, h=6, text=pdf_safe(f"- {r['drug']}: {r['note']}"), align="L")
        pdf.ln(5)
        
    # Drug-Drug Interactions
    interactions = report.get("clinical_interactions", [])
    if interactions:
        pdf.set_font("helvetica", style="B", size=12)
        pdf.set_text_color(200, 0, 0)
        pdf.set_x(10)
        pdf.cell(0, 10, "Checking for DRUG-DRUG INTERACTIONS", ln=1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", size=10)
        for ddi in interactions:
            pdf.set_x(10)
            pdf.multi_cell(w=0, h=6, text=pdf_safe(f"[{ddi['severity']}] {ddi['drugs']}: {ddi['description']}"), align="L")
        pdf.ln(5)
        
    # Regimen Profiles
    pdf.set_font("helvetica", style="B", size=12)
    pdf.set_x(10)
    pdf.cell(0, 10, "Predictive Clinical Alerts & Profiles", ln=1)
    for profile in report.get("regimen_profiles", []):
        pdf.set_font("helvetica", style="B", size=11)
        pdf.set_x(10)
        pdf.cell(0, 8, text=pdf_safe(f"Drug: {profile.get('generic', 'Unknown').capitalize()}"), ln=1)
        
        # Inject Phase 1 Data Blocks
        pdf.set_font("helvetica", size=10)
        pdf.set_x(10)
        pdf.multi_cell(w=0, h=6, text=pdf_safe(f"[DRUG CLASSIFICATION]: {', '.join(profile.get('classification', ['N/A']))}"), align="L")
        pdf.set_x(10)
        pdf.multi_cell(w=0, h=6, text=pdf_safe(f"[RoA]: {', '.join(profile.get('roa', ['Unspecified']))}"), align="L")
        pdf.set_x(10)
        pdf.multi_cell(w=0, h=6, text=pdf_safe(f"[PGx MARKERS FOUND] Targets: {', '.join(profile.get('pgx_markers', ['None']))}"), align="L")
        pdf.set_x(10)
        pdf.multi_cell(w=0, h=6, text=pdf_safe(f"[FDA] CLINICAL HIGHLIGHTS: {profile.get('clinical_highlights', 'N/A')}"), align="L")
        
        alerts = profile.get("predictive_alerts", [])
        if alerts:
            pdf.ln(2)
            for alert in alerts:
                pdf.set_x(10)
                pdf.multi_cell(w=0, h=6, text=pdf_safe(f"  > {alert}"), align="L")
        pdf.ln(5)
            
    return bytes(pdf.output())

# --- SIDEBAR NAVIGATION ---
page = st.sidebar.radio("Module Selection", ["⚕️ Clinical Workstation", "📊 Analytics Dashboard"])

if page == "⚕️ Clinical Workstation":
    st.title("⚕️ Clinical Informatics Logic Engine (CILE)")
    st.markdown("---")

    # Row 1: Demographics
    st.subheader("Patient Demographics")
    col1, col2 = st.columns(2)
    age = col1.number_input("Patient Age", min_value=1, max_value=120, value=1, step=1)
    gender = col2.selectbox("Gender", ["M", "F"])

    # Row 2: Vitals
    st.subheader("Clinical Vitals")
    col3, col4, col5 = st.columns(3)
    weight = col3.number_input("Weight (kg) Leave it empty if not provided:", min_value=0.0, value=0.0, step=1.0)
    srcr = col4.number_input("Serum Creatinine (mg/dL) Leave it empty if not provided:", min_value=0.0, value=0.0, step=0.1)
    hba1c = col5.number_input("HbA1c (%) Leave it empty if not provided:", min_value=0.0, value=0.0, step=0.1)

    st.markdown("---")

    # Row 3: Regimen Input
    st.subheader("Medication Regimen")
    st.info("Enter one medication per line. For prevention drugs (e.g., Aspirin, Statins), add '-p' for Primary or '-s' for Secondary prevention. Example: `aspirin -p`")

    regimen_text = st.text_area("Enter Drug List", height=180)

    # Execution
    if st.button("Execute Clinical Analysis", type="primary"):
        if not regimen_text.strip():
            st.warning("Enter at least one medication.")
        else:
            regimen = []
            for line in regimen_text.split('\n'):
                line = line.strip().lower()
                if not line: continue
                
                # Parse intervention tags
                ind_val = None
                if '-p' in line:
                    ind_val = 'p'
                    line = line.replace('-p', '').strip()
                elif '-s' in line:
                    ind_val = 's'
                    line = line.replace('-s', '').strip()
                    
                regimen.append({"name": line, "indication": ind_val})
                
            payload = {
                "age": age, "gender": gender, "weight": weight, 
                "srcr": srcr, "hba1c": hba1c, "regimen": regimen
            }
            
            headers = {"x-api-key": INTERNAL_KEY}
            with st.spinner("Transmitting to CILE secure server..."):
                try:
                    response = requests.post(API_URL, json=payload, headers=headers, timeout=90)
                    response.raise_for_status()
                    report = response.json()
                    
                    st.success("Analysis Complete")
                    st.markdown("### Clinical Findings")
                    
                    # 1. Renal Alerts
                    renal_alerts = report.get("renal_alerts", [])
                    if renal_alerts:
                        st.error("**Renal Dose Adjustments Required:**")
                        for r in renal_alerts:
                            st.write(f"- **{r['drug']}**: {r['note']}")       
                            
                    # 2. Drug-Drug Interactions
                    ddis = report.get("clinical_interactions", [])
                    if ddis:
                        st.warning("**Critical Drug Interactions:**")
                        for ddi in ddis:
                            st.write(f"- [{ddi['severity']}] **{ddi['drugs']}**: {ddi['description']}")
                            
                    # 3. Predictive Clinical Alerts & Profiles
                    st.markdown("### Predictive Clinical Alerts & Profiles")
                    for profile in report.get("regimen_profiles", []):
                        with st.expander(f"{profile.get('generic', 'Unknown').capitalize()} Clinical Profile", expanded=True):
                            st.markdown(f"**[DRUG CLASSIFICATION]:** {', '.join(profile.get('classification', ['N/A']))}")
                            st.markdown(f"**[RoA]:** {', '.join(profile.get('roa', ['Unspecified']))}")
                            st.markdown(f"**[PGx MARKERS FOUND] Targets:** {', '.join(profile.get('pgx_markers', ['None']))}")
                            st.markdown(f"**[FDA] CLINICAL HIGHLIGHTS:** {profile.get('clinical_highlights', 'N/A')}")
                            st.markdown("---")
                            alerts = profile.get("predictive_alerts", [])
                            if alerts:
                                for alert in alerts:
                                    st.warning(alert)
                            else:
                                st.success("No critical demographic or condition-based alerts triggered.")
                    
                    # --- DUAL EXPORT CONTROLS ---
                    st.markdown("### Export Clinical Data")
                    export_col1, export_col2 = st.columns(2)
                    
                    # 1. Human-Readable PDF
                    try:
                        pdf_bytes = generate_clinical_pdf(report)
                        export_col1.download_button(
                            label="Download PDF Report 📄",
                            data=pdf_bytes,
                            file_name=f"CILE_Consult_{age}{gender}.pdf",
                            mime="application/pdf"
                        )
                    except Exception:
                        st.error("An error occurred during document compilation. Please contact CILE's developer.")
                    
                    # 2. Machine-Readable JSON (FHIR-Ready)
                    fhir_payload = json.dumps(report, indent=4)
                    export_col2.download_button(
                        label="Download FHIR-Interoperable JSON file 📁",
                        data=fhir_payload,
                        file_name=f"CILE_FHIR_{age}{gender}.json",
                        mime="application/json"
                    )
                    
                except requests.exceptions.Timeout:
                    st.error("Server Timeout. Please wait 30 seconds and click 'Execute' again.")
                except requests.exceptions.ConnectionError:
                    st.error(f"Connection Error: Cannot reach {API_URL}.")
                except Exception:
                    st.error("An error occurred. Please contact with CILE's developer.")

elif page == "📊 Analytics Dashboard":
    st.title("📊 Clinical Encounters & Analytics")
    st.markdown("Real-time monitoring of CILE interventions.")
    st.markdown("---")

    try:
        analytics_url = API_URL.replace("/analyze", "/analytics")
        headers = {"x-api-key": INTERNAL_KEY}
        response = requests.get(analytics_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)

        if not df.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Encounters", len(df))
            col2.metric("Total Critical Alerts", int(df['critical_alerts_triggered'].sum()))
            col3.metric("Avg Drugs per Regimen", round(df['drug_count'].mean(), 1))
            
            st.markdown("### Raw Telemetry Log")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No clinical encounters logged yet.")

    except Exception as e:
        st.error(f"Could not connect to Analytics Engine: {e}")